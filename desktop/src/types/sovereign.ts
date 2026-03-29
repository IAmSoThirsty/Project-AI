export type WorkspaceEntryKind = 'file' | 'directory';

export interface WorkspaceEntry {
  name: string;
  path: string;
  kind: WorkspaceEntryKind;
  extension: string;
  size: number;
  modifiedAt: number;
}

export interface WorkspaceFile {
  path: string;
  content: string;
  isBinary: boolean;
  tooLarge: boolean;
  size: number;
  modifiedAt: number;
}

export interface RepoStatus {
  branch: string;
  modifiedCount: number;
  untrackedCount: number;
  conflictedCount: number;
  clean: boolean;
  summary: string[];
}

export interface TerminalSessionInfo {
  id: string;
  cwd: string;
  shell: string;
}

export interface TerminalOutputEvent {
  id: string;
  stream: 'stdout' | 'stderr';
  data: string;
}

export interface TerminalExitEvent {
  id: string;
  code: number | null;
}

export interface LegionMessage {
  id: string;
  role: 'system' | 'user' | 'conference';
  title: string;
  body: string;
  route: string[];
  timestamp: string;
}

export interface OfficeFloor {
  id: number;
  name: string;
  specialty: string;
  head: string;
  agents: string[];
  accent: string;
  overview: string;
}

export interface WorkOrderPlan {
  primaryFloor: string;
  supportFloors: string[];
  district: string;
  crew: string[];
  summary: string;
}

export type WorkOrderUrgency = 'routine' | 'priority' | 'critical';
export type WorkOrderStatus = 'conference' | 'active' | 'monitoring';

export interface WorkOrder {
  id: string;
  title: string;
  summary: string;
  target: string;
  district: string;
  assignedFloor: string;
  supportFloors: string[];
  urgency: WorkOrderUrgency;
  status: WorkOrderStatus;
  createdAt: string;
}

export type CityTwinScenarioKind = 'drift' | 'virus' | 'honeypot' | 'recovery';
export type CityTwinIncidentStatus = 'active' | 'contained' | 'monitoring';

export interface CityTwinIncident {
  id: string;
  title: string;
  detail: string;
  kind: CityTwinScenarioKind;
  district: string;
  assignedFloor: string;
  severity: number;
  status: CityTwinIncidentStatus;
  createdAt: string;
}

export interface CityTwinDistrict {
  id: string;
  label: string;
  focus: string;
  assignedFloor: string;
  drift: number;
  defense: number;
  throughput: number;
  incidentCount: number;
  queueDepth: number;
  highlighted: boolean;
}

export type WaterfallSearchEngine = 'duckduckgo' | 'startpage' | 'kagi';
export type WaterfallSearchProvider = 'duckduckgo' | 'startpage' | 'kagi' | string;

export interface WaterfallSearchQuery {
  query: string;
  regionBias: string;
  safeSearch: boolean;
  recencyBiasHours: number;
  providers: WaterfallSearchProvider[];
}

export interface WaterfallSearchResult {
  id: string;
  title: string;
  url: string;
  snippet: string;
  provider: WaterfallSearchProvider;
  published: string;
  relevanceScore: number;
  categories: string[];
}

export interface WaterfallSearchResponse {
  results: WaterfallSearchResult[];
  totalHits: number;
  queryId: string;
  warnings: string[];
}

export interface WaterfallConsigliereAuditRequest {
  query: WaterfallSearchQuery;
  rawResults: WaterfallSearchResult[];
}

export interface WaterfallConsigliereAuditResponse {
  privacyFlags: string[];
  sourceClusters: string[];
  explanationCards: string[];
  optionalSummaries: Record<string, string>;
}

export interface WaterfallSecurityStatus {
  vpnEnabled: boolean;
  firewallProfiles: string[];
  microvmHealth: 'unknown' | 'nominal' | 'degraded' | 'offline';
  ledgerHead: string;
  downloadGateOnline: boolean;
  orchestratorMode: 'offline' | 'connecting' | 'online' | 'fallback';
  warnings: string[];
}

export interface WaterfallVpnStateRequest {
  enabled: boolean;
  server: string;
}

export interface WaterfallDownloadScanRequest {
  path: string;
  sha256: string;
}

export interface WaterfallPrivacyEvent {
  type: string;
  summary: string;
  target: string;
  timestamp: number;
  metadata: Record<string, string>;
}

export interface WaterfallUpdateManifest {
  version: string;
  signature: string;
  url: string;
  channel: string;
  available: boolean;
  notes: string[];
  integrityState: 'unknown' | 'verified' | 'unverified';
  artifactSha256?: string;
  artifactName?: string;
  publishedAt?: string;
  manifestVerifiedAt?: number;
  stageStatus?: 'idle' | 'staged' | 'failed';
  stagedArtifactPath?: string;
  rollbackReady?: boolean;
  statusMessage?: string;
}

export interface WaterfallBridgeHealth {
  connected: boolean;
  protocolVersion: string;
  transport: 'named-pipe' | 'unix-domain-socket' | 'tcp-loopback';
  endpoint: string;
  capabilities: string[];
  mode: 'offline' | 'connecting' | 'online' | 'fallback';
  lastError?: string;
  lastHandshakeAt?: number;
}

export interface CollectiveContributionSettings {
  enabled: boolean;
  cpuEnabled: boolean;
  gpuEnabled: boolean;
  cpuLimitPercent: number;
  gpuLimitPercent: number;
  requireIdle: boolean;
  requireAC: boolean;
  sessionCapMinutes: number;
}

export interface WaterfallPrivacySettings {
  doNotTrack: boolean;
  globalPrivacyControl: boolean;
  blockTrackers: boolean;
  httpsOnlyMode: boolean;
  masterKillSwitch: boolean;
  permissionsLockdown: boolean;
  stripReferrers: boolean;
  antiFingerprinting: boolean;
  blockPopups: boolean;
  clearDataOnExit: boolean;
  blockedHosts: string[];
}

export interface WaterfallNetworkSettings {
  proxyMode: 'system' | 'manual';
  proxyRules: string;
  proxyBypassRules: string;
}

export interface WaterfallSecurityWorkbenchSettings {
  scanDownloadsOnStart: boolean;
  scanDownloadsOnCompletion: boolean;
  quarantineHighRiskDownloads: boolean;
  strictScopeMode: boolean;
  nativeArtifactScanning: boolean;
  externalAuthorizedScanning: boolean;
  exportEvidenceBundles: boolean;
}

export interface WaterfallAccountProfile {
  displayName: string;
  deviceName: string;
  nodeId: string;
  profileVersion: string;
}

export interface WaterfallPeerRecord {
  id: string;
  displayName: string;
  addedAt: number;
}

export interface WaterfallMeshProfile {
  protocolVersion: string;
  trustMode: 'invite-only';
  peers: WaterfallPeerRecord[];
}

export interface WaterfallBrowserSettings {
  homePage: string;
  searchEngine: WaterfallSearchEngine;
  restoreSession: boolean;
  collective: CollectiveContributionSettings;
  privacy: WaterfallPrivacySettings;
  network: WaterfallNetworkSettings;
  security: WaterfallSecurityWorkbenchSettings;
  account: WaterfallAccountProfile;
  mesh: WaterfallMeshProfile;
}

export interface WaterfallGpuDevice {
  name: string;
  vendor: string;
  active: boolean;
}

export interface WaterfallResourceProfile {
  platform: string;
  architecture: string;
  cpu: {
    model: string;
    cores: number;
    speedMhz: number;
  };
  memory: {
    totalGb: number;
    freeGb: number;
  };
  gpu: {
    devices: WaterfallGpuDevice[];
    activeDeviceCount: number;
  };
}

export interface WaterfallBookmark {
  id: string;
  title: string;
  url: string;
  createdAt: number;
}

export interface WaterfallHistoryEntry {
  id: string;
  title: string;
  url: string;
  visitedAt: number;
}

export interface WaterfallTabState {
  id: string;
  title: string;
  url: string;
  loading: boolean;
  canGoBack: boolean;
  canGoForward: boolean;
  lastVisitedAt: number;
}

export interface WaterfallNativeControlOption {
  value: string;
  label: string;
}

export interface WaterfallNativeRenderBox {
  nodePath: string;
  role: string;
  x: number;
  y: number;
  width: number;
  height: number;
  zIndex: number;
  focusIndex: number | null;
  text: string | null;
  surface: string | null;
  tone: string | null;
  layout: 'stack' | 'grid' | 'columns' | null;
  emphasis: string | null;
  interactive: boolean;
  href: string | null;
  actionId: string | null;
  controlKind: 'text' | 'select' | 'range' | null;
  settingPath: WaterfallNativeSettingPath | null;
  controlLabel: string | null;
  controlCaption: string | null;
  controlStringValue: string | null;
  controlNumberValue: number | null;
  controlPlaceholder: string | null;
  controlMin: number | null;
  controlMax: number | null;
  controlStep: number | null;
  controlOptions: WaterfallNativeControlOption[];
}

export interface WaterfallNativeRenderResult {
  route: string;
  title: string;
  subtitle: string;
  markup: string;
  viewportWidth: number;
  documentHeight: number;
  boxes: WaterfallNativeRenderBox[];
  engine: {
    engineId: string;
    integration: string;
    focus: string[];
  };
}

export interface WaterfallNativeDocument {
  route: string;
  title: string;
  subtitle: string;
  markup: string;
}

export type WaterfallNativeSettingPath =
  | 'homePage'
  | 'searchEngine'
  | 'restoreSession'
  | 'privacy.doNotTrack'
  | 'privacy.globalPrivacyControl'
  | 'privacy.blockTrackers'
  | 'privacy.httpsOnlyMode'
  | 'privacy.masterKillSwitch'
  | 'privacy.permissionsLockdown'
  | 'privacy.stripReferrers'
  | 'privacy.antiFingerprinting'
  | 'privacy.blockPopups'
  | 'security.scanDownloadsOnStart'
  | 'security.scanDownloadsOnCompletion'
  | 'security.quarantineHighRiskDownloads'
  | 'security.strictScopeMode'
  | 'security.nativeArtifactScanning'
  | 'security.externalAuthorizedScanning'
  | 'security.exportEvidenceBundles'
  | 'collective.enabled'
  | 'collective.cpuEnabled'
  | 'collective.gpuEnabled'
  | 'collective.cpuLimitPercent'
  | 'collective.gpuLimitPercent'
  | 'collective.sessionCapMinutes';

export type WaterfallNativeRouteActionKind =
  | 'navigate'
  | 'open-settings'
  | 'show-download'
  | 'scan-download'
  | 'release-download-quarantine'
  | 'remove-extension'
  | 'add-extension'
  | 'copy-node-id'
  | 'reset-session'
  | 'refresh'
  | 'export-security-report'
  | 'export-bounty-pack'
  | 'enable-vpn'
  | 'disable-vpn'
  | 'toggle-setting'
  | 'set-setting'
  | 'toggle-bookmark'
  | 'create-tab'
  | 'clear-history'
  | 'navigate-back'
  | 'navigate-forward'
  | 'check-updates'
  | 'apply-update';

export interface WaterfallNativeRouteAction {
  id: string;
  title: string;
  caption: string;
  kind: WaterfallNativeRouteActionKind;
  target?: string;
  downloadId?: string;
  filePath?: string;
  extensionPath?: string;
  settingPath?: WaterfallNativeSettingPath;
  settingValue?: boolean;
  stringValue?: string;
  numberValue?: number;
}

export interface WaterfallBrowserSession {
  tabs: WaterfallTabState[];
  activeTabId: string;
  bookmarks: WaterfallBookmark[];
  history: WaterfallHistoryEntry[];
}

export type WaterfallDownloadStatus =
  | 'progressing'
  | 'completed'
  | 'cancelled'
  | 'interrupted';

export type WaterfallSecurityScope = 'native' | 'foreign';
export type WaterfallSecurityScanStage = 'preflight' | 'postflight';
export type WaterfallSecurityVerdict = 'pending' | 'clean' | 'review' | 'quarantined';
export type WaterfallSecurityRiskLevel = 'low' | 'moderate' | 'high' | 'critical';

export interface WaterfallDownloadGateVerdict {
  verdict: string;
  riskScore: number;
  findings: string[];
  recommendedAction: string;
}

export interface WaterfallDownloadSecurityScan {
  stage: WaterfallSecurityScanStage;
  scope: WaterfallSecurityScope;
  verdict: WaterfallSecurityVerdict;
  riskLevel: WaterfallSecurityRiskLevel;
  riskScore: number;
  findings: string[];
  scannedAt: number;
  recommendedAction: string;
  quarantined: boolean;
}

export interface WaterfallDownloadRecord {
  id: string;
  filename: string;
  url: string;
  filePath: string;
  originalFilePath?: string;
  quarantinePath?: string;
  mimeType: string;
  status: WaterfallDownloadStatus;
  receivedBytes: number;
  totalBytes: number;
  startedAt: number;
  completedAt?: number;
  quarantinedAt?: number;
  evidenceBundlePath?: string;
  securityScan?: WaterfallDownloadSecurityScan;
}

export interface WaterfallExtensionRecord {
  id: string;
  name: string;
  version: string;
  path: string;
  description: string;
  enabled: boolean;
  loadError?: string;
}

export interface WaterfallProfileBundle {
  version: number;
  exportedAt: number;
  settings: WaterfallBrowserSettings;
  session: WaterfallBrowserSession;
}

export interface WaterfallEncryptedProfileBundle {
  format: 'waterfall.bundle.v1';
  version: 'v1';
  createdAt: string;
  exportId: string;
  authMode: 'passphrase-v1' | 'local-secret-v1';
  cipher: 'aes-256-gcm';
  kdf: {
    algorithm: 'pbkdf2-sha512';
    iterations: number;
    salt: string;
  };
  nonce: string;
  tag: string;
  payloadSha256: string;
  signature: {
    algorithm: 'hmac-sha256';
    value: string;
    scope: 'export-passphrase' | 'local-cache-secret';
  };
  ciphertext: string;
}

export interface WaterfallSecurityReport {
  generatedAt: number;
  browserProfile: string;
  nodeId: string;
  orchestratorStatus?: WaterfallSecurityStatus;
  bridgeHealth?: WaterfallBridgeHealth;
  toolkitInventory?: WaterfallSecurityToolkitInventory;
  summary: {
    totalDownloads: number;
    clean: number;
    review: number;
    quarantined: number;
  };
  settings: {
    privacy: WaterfallPrivacySettings;
    security: WaterfallSecurityWorkbenchSettings;
  };
  downloads: WaterfallDownloadRecord[];
}

export interface WaterfallSecurityToolkitCategory {
  name: string;
  toolCount: number;
  sampleEntries: string[];
}

export interface WaterfallSecurityToolkitInventory {
  available: boolean;
  rootPath: string;
  categoryCount: number;
  toolkitCount: number;
  categories: WaterfallSecurityToolkitCategory[];
}
