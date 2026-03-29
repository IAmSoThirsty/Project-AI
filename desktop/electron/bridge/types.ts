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

export type OrchestratorMethod =
  | 'Ping'
  | 'Query'
  | 'AuditWithConsigliere'
  | 'GetSecurityStatus'
  | 'SetVPNState'
  | 'TriggerDownloadGateScan'
  | 'RecordPrivacyEvent'
  | 'CheckForUpdates'
  | 'ApplyUpdate';

export interface WaterfallPingResponse {
  ok: boolean;
  version: string;
  protocolVersion: string;
  capabilities: string[];
}

export interface OrchestratorBridgeRequestOptions {
  timeoutMs?: number;
  capabilities?: string[];
}

export interface OrchestratorBridgeIpcEndpoint {
  path: string;
  transport: Extract<WaterfallBridgeHealth['transport'], 'named-pipe' | 'unix-domain-socket'>;
}

export interface OrchestratorBridgeTcpEndpoint {
  host: string;
  port: number;
  transport: Extract<WaterfallBridgeHealth['transport'], 'tcp-loopback'>;
}

export type OrchestratorBridgeEndpoint =
  | OrchestratorBridgeIpcEndpoint
  | OrchestratorBridgeTcpEndpoint;

export interface OrchestratorBridgeOptions {
  workspaceRoot: string;
  protocolVersion: string;
  clientName: string;
  requestedCapabilities: string[];
  endpoint?: OrchestratorBridgeEndpoint;
  maxFrameBytes?: number;
  connectionAttempts?: number;
  connectionBackoffMs?: number;
}

export interface BridgeMethodMap {
  Ping: {
    request: Record<string, never>;
    response: WaterfallPingResponse;
  };
  Query: {
    request: WaterfallSearchQuery;
    response: WaterfallSearchResponse;
  };
  AuditWithConsigliere: {
    request: WaterfallConsigliereAuditRequest;
    response: WaterfallConsigliereAuditResponse;
  };
  GetSecurityStatus: {
    request: Record<string, never>;
    response: WaterfallSecurityStatus;
  };
  SetVPNState: {
    request: WaterfallVpnStateRequest;
    response: Record<string, never>;
  };
  TriggerDownloadGateScan: {
    request: WaterfallDownloadScanRequest;
    response: WaterfallDownloadGateVerdict;
  };
  RecordPrivacyEvent: {
    request: WaterfallPrivacyEvent;
    response: Record<string, never>;
  };
  CheckForUpdates: {
    request: Record<string, never>;
    response: WaterfallUpdateManifest;
  };
  ApplyUpdate: {
    request: WaterfallUpdateManifest;
    response: Record<string, never>;
  };
}
