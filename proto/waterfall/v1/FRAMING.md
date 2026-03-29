# WaterFall Control-Plane Framing

WaterFall's local orchestrator transport uses a small length-prefixed binary frame
on top of a local named pipe or Unix domain socket.

## Transport

- Windows: `\\\\.\\pipe\\waterfall-orchestrator-v1`
- macOS/Linux: `${XDG_RUNTIME_DIR:-/tmp}/waterfall-orchestrator-v1.sock`

## Frame format

Each message written to the socket is:

1. A 4-byte unsigned big-endian length prefix.
2. The protobuf-encoded payload bytes.

The payload is one of:

- `BridgeHandshakeRequest`
- `BridgeHandshakeResponse`
- `BridgeRequestEnvelope`
- `BridgeResponseEnvelope`

## Request flow

1. Electron `main` opens the socket and sends a `BridgeHandshakeRequest`.
2. The orchestrator replies with `BridgeHandshakeResponse`.
3. Electron wraps method calls inside `BridgeRequestEnvelope` messages.
4. The orchestrator replies with a matching `BridgeResponseEnvelope`.

`request_id` is mandatory for correlation. The bridge rejects frames above the local
maximum payload limit enforced by the Electron gateway.
