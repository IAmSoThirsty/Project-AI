import type {
  RepoStatus,
  TerminalExitEvent,
  TerminalOutputEvent,
  TerminalSessionInfo,
  WaterfallBridgeHealth,
  WaterfallBrowserSettings,
  WaterfallBrowserSession,
  WaterfallConsigliereAuditRequest,
  WaterfallConsigliereAuditResponse,
  WaterfallDownloadRecord,
  WaterfallDownloadScanRequest,
  WaterfallNativeDocument,
  WaterfallNativeRenderResult,
  WaterfallProfileBundle,
  WaterfallResourceProfile,
  WaterfallSearchQuery,
  WaterfallSearchResponse,
  WaterfallSecurityStatus,
  WaterfallSecurityToolkitInventory,
  WaterfallUpdateManifest,
  WaterfallVpnStateRequest,
  WorkspaceEntry,
  WorkspaceFile
} from './sovereign';

declare global {
  interface Window {
    electron?: {
      window: {
        minimize: () => Promise<void>;
        maximize: () => Promise<void>;
        close: () => Promise<void>;
      };
      store: {
        get: <T = any>(key: string) => Promise<T>;
        set: (key: string, value: any) => Promise<void>;
      };
      app: {
        getVersion: () => Promise<string>;
      };
      browser: {
        openExternal: (targetUrl: string) => Promise<void>;
        applySettings: (settings: WaterfallBrowserSettings) => Promise<void>;
        getDownloads: () => Promise<WaterfallDownloadRecord[]>;
        showDownloadItem: (filePath: string) => Promise<void>;
        scanDownloadRecord: (downloadId: string) => Promise<WaterfallDownloadRecord>;
        releaseDownloadQuarantine: (downloadId: string) => Promise<WaterfallDownloadRecord>;
        exportSecurityReport: () => Promise<string>;
        exportBountyPack: () => Promise<string>;
        getSecurityToolkitInventory: () => Promise<WaterfallSecurityToolkitInventory>;
        onDownloadUpdated: (handler: (event: WaterfallDownloadRecord) => void) => () => void;
        getExtensions: () => Promise<any[]>;
        addExtension: () => Promise<any[]>;
        removeExtension: (extensionPath: string) => Promise<any[]>;
        renderInternalRoute: (
          targetUrl: string,
          viewportWidth?: number
        ) => Promise<WaterfallNativeRenderResult>;
        renderMarkupDocument: (
          document: WaterfallNativeDocument,
          viewportWidth?: number
        ) => Promise<WaterfallNativeRenderResult>;
      };
      system: {
        getResourceProfile: () => Promise<WaterfallResourceProfile>;
      };
      workspace: {
        getRoot: () => Promise<string>;
        getRepoStatus: () => Promise<RepoStatus>;
        listDirectory: (targetPath?: string) => Promise<WorkspaceEntry[]>;
        searchFiles: (query: string) => Promise<WorkspaceEntry[]>;
        readFile: (targetPath: string) => Promise<WorkspaceFile>;
        writeFile: (targetPath: string, content: string) => Promise<WorkspaceFile>;
      };
      terminal: {
        createSession: () => Promise<TerminalSessionInfo>;
        write: (sessionId: string, input: string) => Promise<void>;
        kill: (sessionId: string) => Promise<void>;
        onData: (handler: (event: TerminalOutputEvent) => void) => () => void;
        onExit: (handler: (event: TerminalExitEvent) => void) => () => void;
      };
    };
    waterfall?: {
      orchestrator: {
        getBridgeHealth: () => Promise<WaterfallBridgeHealth>;
        ping: () => Promise<unknown>;
      };
      search: {
        query: (query: WaterfallSearchQuery) => Promise<WaterfallSearchResponse>;
        getCachedResults: (
          query: WaterfallSearchQuery
        ) => Promise<WaterfallSearchResponse | null>;
        audit: (
          request: WaterfallConsigliereAuditRequest
        ) => Promise<WaterfallConsigliereAuditResponse>;
      };
      security: {
        getStatus: () => Promise<WaterfallSecurityStatus>;
        setVPNState: (request: WaterfallVpnStateRequest) => Promise<unknown>;
        scanDownload: (request: WaterfallDownloadScanRequest) => Promise<unknown>;
      };
      ledger: {
        recordEvent: (event: unknown) => Promise<unknown>;
      };
      updates: {
        check: () => Promise<WaterfallUpdateManifest | null>;
        apply: (manifest: WaterfallUpdateManifest) => Promise<WaterfallUpdateManifest>;
      };
      profile: {
        exportBundle: (profile: WaterfallProfileBundle, passphrase: string) => Promise<string>;
        importBundle: (passphrase: string) => Promise<WaterfallProfileBundle>;
      };
    };
  }
}

export {};
