import { EventEmitter } from 'events';
import { randomUUID } from 'crypto';
import type { Socket } from 'net';
import type {
  WaterfallBridgeHealth,
  WaterfallConsigliereAuditRequest,
  WaterfallConsigliereAuditResponse,
  WaterfallDownloadGateVerdict,
  WaterfallDownloadScanRequest,
  WaterfallPrivacyEvent,
  WaterfallSearchQuery,
  WaterfallSearchResponse,
  WaterfallSecurityStatus,
  WaterfallUpdateManifest,
  WaterfallVpnStateRequest
} from '../../src/types/sovereign';
import { loadWaterfallBridgeSchema } from './codec';
import {
  attachLengthPrefixedReader,
  connectWithRetry,
  DEFAULT_MAX_FRAME_BYTES,
  formatOrchestratorEndpoint,
  getOrchestratorEndpoint,
  writeLengthPrefixedFrame
} from './socket';
import type {
  BridgeMethodMap,
  OrchestratorBridgeOptions,
  OrchestratorBridgeRequestOptions,
  OrchestratorMethod,
  WaterfallPingResponse
} from './types';

type PendingRequest = {
  method: OrchestratorMethod;
  resolve: (value: unknown) => void;
  reject: (reason?: unknown) => void;
  timer: NodeJS.Timeout;
};

type PendingHandshake = {
  resolve: (value: {
    accepted: boolean;
    protocolVersion: string;
    serviceVersion: string;
    grantedCapabilities: string[];
    message: string;
  }) => void;
  reject: (reason?: unknown) => void;
  timer: NodeJS.Timeout;
};

export class OrchestratorBridge extends EventEmitter {
  private readonly codec;

  private readonly endpoint: ReturnType<typeof getOrchestratorEndpoint>;

  private readonly pendingRequests = new Map<string, PendingRequest>();

  private pendingHandshake: PendingHandshake | null = null;

  private socket: Socket | null = null;

  private connectPromise: Promise<WaterfallBridgeHealth> | null = null;

  private health: WaterfallBridgeHealth;

  constructor(private readonly options: OrchestratorBridgeOptions) {
    super();
    this.codec = loadWaterfallBridgeSchema(options.workspaceRoot);
    this.endpoint = options.endpoint ?? getOrchestratorEndpoint();
    this.health = {
      connected: false,
      protocolVersion: options.protocolVersion,
      transport: this.endpoint.transport,
      endpoint: formatOrchestratorEndpoint(this.endpoint),
      capabilities: [],
      mode: 'offline'
    };
  }

  getHealth() {
    return {
      ...this.health,
      capabilities: [...this.health.capabilities]
    };
  }

  private setHealth(patch: Partial<WaterfallBridgeHealth>) {
    this.health = {
      ...this.health,
      ...patch
    };
    this.emit('health', this.getHealth());
  }

  async connect() {
    if (this.socket && !this.socket.destroyed && this.health.connected) {
      return this.getHealth();
    }

    if (this.connectPromise) {
      return this.connectPromise;
    }

    this.setHealth({
      mode: 'connecting',
      connected: false
    });

    this.connectPromise = (async () => {
      try {
        const socket = await connectWithRetry(
          this.endpoint,
          this.options.connectionAttempts ?? 5,
          this.options.connectionBackoffMs ?? 300
        );

        socket.setNoDelay(true);
        socket.setTimeout(0);
        this.socket = socket;
        attachLengthPrefixedReader(
          socket,
          (frame) => {
            this.handleFrame(frame);
          },
          (error) => {
            this.handleSocketError(error);
          },
          this.options.maxFrameBytes ?? DEFAULT_MAX_FRAME_BYTES
        );
        socket.on('close', () => {
          this.handleSocketClosed();
        });
        socket.on('error', (error) => {
          this.handleSocketError(error);
        });

        const handshake = await this.performHandshake();
        if (!handshake.accepted) {
          throw new Error(handshake.message || 'WaterFall bridge handshake was rejected.');
        }

        this.setHealth({
          connected: true,
          mode: 'online',
          protocolVersion: handshake.protocolVersion || this.options.protocolVersion,
          capabilities: handshake.grantedCapabilities,
          lastError: undefined,
          lastHandshakeAt: Date.now()
        });
        this.emit('connected', this.getHealth());
        return this.getHealth();
      } catch (error) {
        const resolvedError = error instanceof Error ? error : new Error(String(error));
        this.setHealth({
          connected: false,
          mode: 'fallback',
          lastError: resolvedError.message
        });
        this.emit('error', resolvedError);
        throw resolvedError;
      } finally {
        this.connectPromise = null;
      }
    })();

    return this.connectPromise;
  }

  dispose() {
    for (const pending of this.pendingRequests.values()) {
      clearTimeout(pending.timer);
      pending.reject(new Error('WaterFall bridge is shutting down.'));
    }
    this.pendingRequests.clear();

    if (this.pendingHandshake) {
      clearTimeout(this.pendingHandshake.timer);
      this.pendingHandshake.reject(new Error('WaterFall bridge is shutting down.'));
      this.pendingHandshake = null;
    }

    if (this.socket && !this.socket.destroyed) {
      this.socket.destroy();
    }

    this.socket = null;
    this.setHealth({
      connected: false,
      mode: 'offline'
    });
  }

  private async performHandshake() {
    if (!this.socket) {
      throw new Error('WaterFall bridge socket is not connected.');
    }

    const handshakePayload = this.codec.encodeHandshakeRequest({
      protocolVersion: this.options.protocolVersion,
      clientName: this.options.clientName,
      requestedCapabilities: this.options.requestedCapabilities
    });

    const handshakeResponse = new Promise<{
      accepted: boolean;
      protocolVersion: string;
      serviceVersion: string;
      grantedCapabilities: string[];
      message: string;
    }>((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pendingHandshake = null;
        reject(new Error('WaterFall bridge handshake timed out.'));
      }, 5000);

      this.pendingHandshake = {
        resolve,
        reject,
        timer
      };
    });

    writeLengthPrefixedFrame(this.socket, handshakePayload);
    return handshakeResponse;
  }

  private handleFrame(frame: Buffer) {
    if (this.pendingHandshake) {
      const handshake = this.codec.decodeHandshakeResponse(frame);
      clearTimeout(this.pendingHandshake.timer);
      this.pendingHandshake.resolve({
        accepted: Boolean(handshake.accepted),
        protocolVersion: String(handshake.protocolVersion || ''),
        serviceVersion: String(handshake.serviceVersion || ''),
        grantedCapabilities: Array.isArray(handshake.grantedCapabilities)
          ? handshake.grantedCapabilities.map((capability) => String(capability))
          : [],
        message: String(handshake.message || '')
      });
      this.pendingHandshake = null;
      return;
    }

    const envelope = this.codec.decodeResponseEnvelope(frame);
    const method = envelope.method as OrchestratorMethod;
    const pending = this.pendingRequests.get(envelope.requestId);
    if (!pending) {
      return;
    }

    clearTimeout(pending.timer);
    this.pendingRequests.delete(envelope.requestId);

    if (!envelope.ok) {
      pending.reject(
        new Error(
          envelope.errorMessage ||
            envelope.errorCode ||
            `WaterFall bridge request failed for ${envelope.method}.`
        )
      );
      return;
    }

    try {
      const decoded = this.codec.decodeMethodResponse(method, envelope.payload);
      pending.resolve(decoded);
    } catch (error) {
      pending.reject(
        error instanceof Error
          ? error
          : new Error(`WaterFall bridge could not decode ${envelope.method}.`)
      );
    }
  }

  private handleSocketError(error: Error) {
    this.setHealth({
      connected: false,
      mode: 'fallback',
      lastError: error.message
    });
    this.emit('error', error);
  }

  private handleSocketClosed() {
    this.socket = null;
    this.setHealth({
      connected: false,
      mode: 'fallback'
    });
    this.emit('disconnected', this.getHealth());
  }

  async request<M extends OrchestratorMethod>(
    method: M,
    payload: BridgeMethodMap[M]['request'],
    options: OrchestratorBridgeRequestOptions = {}
  ) {
    if (!this.socket || this.socket.destroyed || !this.health.connected) {
      throw new Error('WaterFall bridge is offline.');
    }

    const requestId = randomUUID();
    const timeoutMs = options.timeoutMs ?? 15000;
    const requestPayload = this.codec.encodeMethodRequest(method, payload as Record<string, unknown>);
    const envelope = this.codec.encodeRequestEnvelope({
      requestId,
      method,
      payload: requestPayload,
      timeoutMs,
      capabilities: options.capabilities ?? []
    });

    return new Promise<BridgeMethodMap[M]['response']>((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pendingRequests.delete(requestId);
        reject(new Error(`WaterFall bridge timed out while waiting for ${method}.`));
      }, timeoutMs);

      this.pendingRequests.set(requestId, {
        method,
        resolve: resolve as (value: unknown) => void,
        reject,
        timer
      });

      if (!this.socket) {
        clearTimeout(timer);
        this.pendingRequests.delete(requestId);
        reject(new Error('WaterFall bridge socket went away before the request was written.'));
        return;
      }

      writeLengthPrefixedFrame(this.socket, envelope);
    });
  }

  ping() {
    return this.request('Ping', {}, {
      timeoutMs: 5000,
      capabilities: ['health']
    }) as Promise<WaterfallPingResponse>;
  }

  query(query: WaterfallSearchQuery) {
    return this.request('Query', query, {
      capabilities: ['search']
    }) as Promise<WaterfallSearchResponse>;
  }

  auditWithConsigliere(request: WaterfallConsigliereAuditRequest) {
    return this.request('AuditWithConsigliere', request, {
      capabilities: ['consigliere']
    }) as Promise<WaterfallConsigliereAuditResponse>;
  }

  getSecurityStatus() {
    return this.request('GetSecurityStatus', {}, {
      capabilities: ['security']
    }) as Promise<WaterfallSecurityStatus>;
  }

  setVpnState(request: WaterfallVpnStateRequest) {
    return this.request('SetVPNState', request, {
      capabilities: ['security']
    }) as Promise<Record<string, never>>;
  }

  triggerDownloadGateScan(request: WaterfallDownloadScanRequest) {
    return this.request('TriggerDownloadGateScan', request, {
      timeoutMs: 45000,
      capabilities: ['download-gate']
    }) as Promise<WaterfallDownloadGateVerdict>;
  }

  recordPrivacyEvent(request: WaterfallPrivacyEvent) {
    return this.request('RecordPrivacyEvent', request, {
      capabilities: ['ledger']
    }) as Promise<Record<string, never>>;
  }

  checkForUpdates() {
    return this.request('CheckForUpdates', {}, {
      capabilities: ['updates']
    }) as Promise<WaterfallUpdateManifest>;
  }

  applyUpdate(manifest: WaterfallUpdateManifest) {
    return this.request('ApplyUpdate', manifest, {
      timeoutMs: 45000,
      capabilities: ['updates']
    }) as Promise<Record<string, never>>;
  }
}

export function createOrchestratorBridge(options: OrchestratorBridgeOptions) {
  return new OrchestratorBridge(options);
}
