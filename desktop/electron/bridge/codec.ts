import * as path from 'path';
import * as protobuf from 'protobufjs';
import type { OrchestratorMethod } from './types';

type MethodDefinition = {
  request: string;
  response: string;
};

type EnvelopeRecord = {
  requestId: string;
  method: string;
  payload: Uint8Array;
  timeoutMs?: number;
  capabilities?: string[];
  ok?: boolean;
  errorCode?: string;
  errorMessage?: string;
  warnings?: string[];
};

const METHOD_DEFINITIONS: Record<OrchestratorMethod, MethodDefinition> = {
  Ping: {
    request: 'waterfall.v1.PingRequest',
    response: 'waterfall.v1.PingResponse'
  },
  Query: {
    request: 'waterfall.v1.SearchQuery',
    response: 'waterfall.v1.SearchResponse'
  },
  AuditWithConsigliere: {
    request: 'waterfall.v1.ConsigliereAuditRequest',
    response: 'waterfall.v1.ConsigliereAuditResponse'
  },
  GetSecurityStatus: {
    request: 'waterfall.v1.Empty',
    response: 'waterfall.v1.SecurityStatus'
  },
  SetVPNState: {
    request: 'waterfall.v1.VPNStateRequest',
    response: 'waterfall.v1.Empty'
  },
  TriggerDownloadGateScan: {
    request: 'waterfall.v1.DownloadScanRequest',
    response: 'waterfall.v1.DownloadScanVerdict'
  },
  RecordPrivacyEvent: {
    request: 'waterfall.v1.PrivacyEvent',
    response: 'waterfall.v1.Empty'
  },
  CheckForUpdates: {
    request: 'waterfall.v1.Empty',
    response: 'waterfall.v1.UpdateManifest'
  },
  ApplyUpdate: {
    request: 'waterfall.v1.UpdateManifest',
    response: 'waterfall.v1.Empty'
  }
};

const HANDSHAKE_REQUEST_TYPE = 'waterfall.v1.BridgeHandshakeRequest';
const HANDSHAKE_RESPONSE_TYPE = 'waterfall.v1.BridgeHandshakeResponse';
const REQUEST_ENVELOPE_TYPE = 'waterfall.v1.BridgeRequestEnvelope';
const RESPONSE_ENVELOPE_TYPE = 'waterfall.v1.BridgeResponseEnvelope';

const TO_OBJECT_OPTIONS: protobuf.IConversionOptions = {
  longs: Number,
  enums: String,
  bytes: Buffer,
  defaults: true
};

function assertMessageType(root: protobuf.Root, messageName: string) {
  const candidate = root.lookup(messageName);
  if (!(candidate instanceof protobuf.Type)) {
    throw new Error(`WaterFall bridge could not resolve protobuf type: ${messageName}`);
  }

  return candidate;
}

export function loadWaterfallBridgeSchema(workspaceRoot: string) {
  const schemaPath = path.join(workspaceRoot, 'proto', 'waterfall', 'v1', 'waterfall.proto');
  const root = protobuf.loadSync(schemaPath);
  root.resolveAll();

  const handshakeRequestType = assertMessageType(root, HANDSHAKE_REQUEST_TYPE);
  const handshakeResponseType = assertMessageType(root, HANDSHAKE_RESPONSE_TYPE);
  const requestEnvelopeType = assertMessageType(root, REQUEST_ENVELOPE_TYPE);
  const responseEnvelopeType = assertMessageType(root, RESPONSE_ENVELOPE_TYPE);
  const requestTypes = Object.fromEntries(
    Object.entries(METHOD_DEFINITIONS).map(([method, definition]) => [
      method,
      assertMessageType(root, definition.request)
    ])
  ) as Record<OrchestratorMethod, protobuf.Type>;
  const responseTypes = Object.fromEntries(
    Object.entries(METHOD_DEFINITIONS).map(([method, definition]) => [
      method,
      assertMessageType(root, definition.response)
    ])
  ) as Record<OrchestratorMethod, protobuf.Type>;

  const encode = (type: protobuf.Type, payload: Record<string, unknown>) => {
    const verificationError = type.verify(payload);
    if (verificationError) {
      throw new Error(`WaterFall bridge rejected invalid protobuf payload: ${verificationError}`);
    }

    return Buffer.from(type.encode(type.fromObject(payload)).finish());
  };

  const decode = (type: protobuf.Type, payload: Uint8Array) =>
    type.toObject(type.decode(payload), TO_OBJECT_OPTIONS) as Record<string, unknown>;

  return {
    schemaPath,
    encodeHandshakeRequest(payload: Record<string, unknown>) {
      return encode(handshakeRequestType, payload);
    },
    decodeHandshakeResponse(payload: Uint8Array) {
      return decode(handshakeResponseType, payload);
    },
    encodeRequestEnvelope(payload: EnvelopeRecord) {
      return encode(requestEnvelopeType, {
        requestId: payload.requestId,
        method: payload.method,
        payload: payload.payload,
        timeoutMs: payload.timeoutMs ?? 0,
        capabilities: payload.capabilities ?? []
      });
    },
    decodeResponseEnvelope(payload: Uint8Array) {
      const decoded = decode(responseEnvelopeType, payload);
      return {
        requestId: String(decoded.requestId || ''),
        method: String(decoded.method || ''),
        ok: Boolean(decoded.ok),
        payload: Buffer.from((decoded.payload as Uint8Array | Buffer | undefined) || []),
        errorCode: String(decoded.errorCode || ''),
        errorMessage: String(decoded.errorMessage || ''),
        warnings: Array.isArray(decoded.warnings)
          ? decoded.warnings.map((warning) => String(warning))
          : []
      };
    },
    encodeMethodRequest(method: OrchestratorMethod, payload: Record<string, unknown>) {
      return encode(requestTypes[method], payload);
    },
    decodeMethodResponse(method: OrchestratorMethod, payload: Uint8Array) {
      return decode(responseTypes[method], payload);
    }
  };
}
