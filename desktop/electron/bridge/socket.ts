import * as fs from 'fs';
import * as net from 'net';
import * as path from 'path';
import * as os from 'os';
import type { OrchestratorBridgeEndpoint } from './types';

export const DEFAULT_MAX_FRAME_BYTES = 4 * 1024 * 1024;

function parseConfiguredEndpoint(specification: string): OrchestratorBridgeEndpoint {
  if (specification.startsWith('tcp://')) {
    const parsed = new URL(specification);
    const port = Number(parsed.port);

    if (parsed.hostname !== '127.0.0.1' && parsed.hostname !== 'localhost') {
      throw new Error('WaterFall bridge only accepts loopback TCP endpoints.');
    }

    if (!Number.isInteger(port) || port <= 0 || port > 65535) {
      throw new Error('WaterFall bridge rejected an invalid TCP endpoint port.');
    }

    return {
      host: parsed.hostname,
      port,
      transport: 'tcp-loopback'
    };
  }

  if (process.platform === 'win32') {
    return {
      path: specification,
      transport: 'named-pipe'
    };
  }

  return {
    path: specification,
    transport: 'unix-domain-socket'
  };
}

export function getOrchestratorEndpoint(): OrchestratorBridgeEndpoint {
  const configuredEndpoint = process.env.WATERFALL_ORCHESTRATOR_ENDPOINT?.trim();
  if (configuredEndpoint) {
    return parseConfiguredEndpoint(configuredEndpoint);
  }

  if (process.platform === 'win32') {
    return {
      path: '\\\\.\\pipe\\waterfall-orchestrator-v1',
      transport: 'named-pipe'
    };
  }

  const runtimeDirectory = process.env.XDG_RUNTIME_DIR || os.tmpdir();
  return {
    path: path.join(runtimeDirectory, 'waterfall-orchestrator-v1.sock'),
    transport: 'unix-domain-socket'
  };
}

export function formatOrchestratorEndpoint(endpoint: OrchestratorBridgeEndpoint) {
  if (endpoint.transport === 'tcp-loopback') {
    return `tcp://${endpoint.host}:${endpoint.port}`;
  }

  return endpoint.path;
}

export function removeOrchestratorSocketFile(endpoint: OrchestratorBridgeEndpoint) {
  if (endpoint.transport !== 'unix-domain-socket') {
    return;
  }

  try {
    if (fs.existsSync(endpoint.path)) {
      fs.unlinkSync(endpoint.path);
    }
  } catch {
    // The orchestrator owns cleanup once it is live; stale sockets are best-effort only.
  }
}

export function writeLengthPrefixedFrame(socket: net.Socket, payload: Uint8Array) {
  const body = Buffer.from(payload);
  const lengthPrefix = Buffer.allocUnsafe(4);
  lengthPrefix.writeUInt32BE(body.length, 0);
  socket.write(Buffer.concat([lengthPrefix, body]));
}

export function attachLengthPrefixedReader(
  socket: net.Socket,
  onFrame: (frame: Buffer) => void,
  onError: (error: Error) => void,
  maxFrameBytes = DEFAULT_MAX_FRAME_BYTES
) {
  let buffered = Buffer.alloc(0);

  socket.on('data', (chunk: Buffer) => {
    buffered = Buffer.concat([buffered, chunk]);

    while (buffered.length >= 4) {
      const frameLength = buffered.readUInt32BE(0);

      if (frameLength > maxFrameBytes) {
        onError(new Error(`WaterFall bridge rejected an oversized frame of ${frameLength} bytes.`));
        buffered = Buffer.alloc(0);
        return;
      }

      if (buffered.length < frameLength + 4) {
        return;
      }

      const frame = buffered.subarray(4, frameLength + 4);
      buffered = buffered.subarray(frameLength + 4);
      onFrame(frame);
    }
  });
}

function connectOnce(endpoint: OrchestratorBridgeEndpoint) {
  return new Promise<net.Socket>((resolve, reject) => {
    const socket =
      endpoint.transport === 'tcp-loopback'
        ? net.createConnection({
            host: endpoint.host,
            port: endpoint.port
          })
        : net.createConnection(endpoint.path);

    socket.once('connect', () => {
      socket.removeListener('error', reject);
      resolve(socket);
    });

    socket.once('error', (error) => {
      socket.destroy();
      reject(error);
    });
  });
}

export async function connectWithRetry(
  endpoint: OrchestratorBridgeEndpoint,
  attempts = 5,
  backoffMs = 300
) {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt < attempts; attempt += 1) {
    try {
      return await connectOnce(endpoint);
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      if (attempt < attempts - 1) {
        await new Promise((resolve) => setTimeout(resolve, backoffMs * (attempt + 1)));
      }
    }
  }

  throw lastError || new Error('WaterFall bridge could not reach the orchestrator endpoint.');
}
