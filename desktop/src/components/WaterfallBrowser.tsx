import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Chip,
  Divider,
  Drawer,
  FormControlLabel,
  IconButton,
  InputAdornment,
  MenuItem,
  Slider,
  Stack,
  Switch,
  TextField,
  Typography
} from '@mui/material';
import {
  AccountCircle,
  Add,
  ArrowBack,
  ArrowForward,
  AutoAwesome,
  BookmarkAdd,
  Bolt,
  Close,
  Download,
  Extension,
  Home,
  Hub,
  Launch,
  PrivacyTip,
  Refresh,
  Search,
  Settings,
  Shield,
  Stop,
  TravelExplore,
  UploadFile
} from '@mui/icons-material';
import WaterfallNativeRoutePane from './WaterfallNativeRoutePane';
import type {
  CollectiveContributionSettings,
  WaterfallBridgeHealth,
  WaterfallConsigliereAuditRequest,
  WaterfallConsigliereAuditResponse,
  WaterfallDownloadRecord,
  WaterfallExtensionRecord,
  WaterfallBookmark,
  WaterfallBrowserSession,
  WaterfallBrowserSettings,
  WaterfallHistoryEntry,
  WaterfallNativeDocument,
  WaterfallNativeRouteAction,
  WaterfallNativeSettingPath,
  WaterfallNativeRenderResult,
  WaterfallProfileBundle,
  WaterfallResourceProfile,
  WaterfallSearchQuery,
  WaterfallSearchEngine,
  WaterfallSearchResponse,
  WaterfallSecurityStatus,
  WaterfallSecurityToolkitInventory,
  WaterfallTabState,
  WaterfallUpdateManifest
} from '../types/sovereign';

const WATERFALL_SETTINGS_KEY = 'thirstys.waterfall.settings';
const WATERFALL_SESSION_KEY = 'thirstys.waterfall.session';
const WATERFALL_PARTITION = 'persist:thirstys-waterfall';
const WATERFALL_HOME_ROUTE = 'waterfall://home';
const WATERFALL_SEARCH_ROUTE = 'waterfall://search';
const WATERFALL_SECURITY_WORKBENCH_ROUTE = 'waterfall://security-workbench';
const WATERFALL_SITE_SHIELD_ROUTE = 'waterfall://site-shield';
const WATERFALL_PRIVACY_AUDITOR_ROUTE = 'waterfall://privacy-auditor';
const WATERFALL_SECURITY_ARCHITECT_ROUTE = 'waterfall://security-architect';
const WATERFALL_UPDATES_ROUTE = 'waterfall://updates';

const SEARCH_ENGINE_LABELS: Record<WaterfallSearchEngine, string> = {
  duckduckgo: 'DuckDuckGo',
  startpage: 'Startpage',
  kagi: 'Kagi'
};

const SEARCH_ENGINE_CONTROL_OPTIONS = (
  Object.entries(SEARCH_ENGINE_LABELS) as Array<[WaterfallSearchEngine, string]>
).map(([value, label]) => ({
  value,
  label
}));
const SEARCH_ENGINE_VALUES = SEARCH_ENGINE_CONTROL_OPTIONS.map((option) => option.value);

const isWaterfallRoute = (value: string) => /^waterfall:\/\//i.test(value.trim());
const normalizeWaterfallRoute = (value: string) => {
  const trimmedValue = value.trim();

  if (!trimmedValue) {
    return '';
  }

  try {
    const parsedUrl = new URL(trimmedValue);
    if (parsedUrl.protocol !== 'waterfall:') {
      return trimmedValue.replace(/\/+$/, '').toLowerCase();
    }

    const normalizedHost = parsedUrl.hostname.toLowerCase();
    const normalizedPathname =
      parsedUrl.pathname && parsedUrl.pathname !== '/'
        ? parsedUrl.pathname.replace(/\/+$/, '').toLowerCase()
        : '';

    return `waterfall://${normalizedHost}${normalizedPathname}${parsedUrl.search}${parsedUrl.hash}`;
  } catch {
    return trimmedValue.replace(/\/+$/, '').toLowerCase();
  }
};
const isWaterfallSearchRoute = (value: string) => {
  if (!isWaterfallRoute(value)) {
    return false;
  }

  try {
    const parsedUrl = new URL(value.trim());
    return parsedUrl.hostname.toLowerCase() === 'search';
  } catch {
    return normalizeWaterfallRoute(value).startsWith(WATERFALL_SEARCH_ROUTE);
  }
};
const getWaterfallSearchQuery = (value: string) => {
  if (!isWaterfallSearchRoute(value)) {
    return '';
  }

  try {
    return new URL(value.trim()).searchParams.get('q')?.trim() || '';
  } catch {
    return '';
  }
};
const buildWaterfallSearchRoute = (query: string) => {
  const trimmedQuery = query.trim();

  if (!trimmedQuery) {
    return WATERFALL_SEARCH_ROUTE;
  }

  const searchParams = new URLSearchParams({
    q: trimmedQuery
  });
  return `${WATERFALL_SEARCH_ROUTE}?${searchParams.toString()}`;
};
const getOrderedSearchProviders = (preferredSearchEngine: WaterfallSearchEngine) => [
  preferredSearchEngine,
  ...SEARCH_ENGINE_VALUES.filter((value) => value !== preferredSearchEngine)
];
const escapeNativeText = (value: string) => value.replace(/</g, '(').replace(/>/g, ')');
const escapeNativeAttribute = (value: string) =>
  escapeNativeText(value).replace(/"/g, "'").replace(/`/g, "'");
const formatKilobytes = (bytes: number) => `${Math.max(1, Math.round(bytes / 1024))} KB`;

interface NativeCardOptions {
  title: string;
  body: string;
  href?: string;
  actionId?: string;
  surface?: string;
  tone?: string;
  span?: number;
  emphasis?: string;
}

const buildNativeCard = ({
  title,
  body,
  href,
  actionId,
  surface = 'card',
  tone,
  span,
  emphasis
}: NativeCardOptions) => {
  const attributes = [`data-wf-surface="${escapeNativeAttribute(surface)}"`];

  if (tone) {
    attributes.push(`data-wf-tone="${escapeNativeAttribute(tone)}"`);
  }

  if (typeof span === 'number' && span > 1) {
    attributes.push(`data-wf-span="${Math.max(2, Math.floor(span))}"`);
  }

  if (emphasis) {
    attributes.push(`data-wf-emphasis="${escapeNativeAttribute(emphasis)}"`);
  }

  if (href) {
    attributes.push(`href="${escapeNativeAttribute(href)}"`);
  }

  if (actionId) {
    attributes.push(`data-wf-action="${escapeNativeAttribute(actionId)}"`);
  }

  return `<section ${attributes.join(' ')}><h2>${escapeNativeText(title)}</h2><p>${escapeNativeText(body)}</p></section>`;
};

interface NativeClusterOptions {
  children: string;
  columns?: number;
  surface?: string;
  tone?: string;
  gap?: number;
}

const buildNativeCluster = ({
  children,
  columns = 2,
  surface = 'cluster',
  tone,
  gap = 2
}: NativeClusterOptions) => {
  const attributes = [
    `data-wf-surface="${escapeNativeAttribute(surface)}"`,
    'data-wf-layout="grid"',
    `data-wf-columns="${Math.min(4, Math.max(1, Math.floor(columns)))}"`,
    `data-wf-gap="${Math.min(4, Math.max(1, Math.floor(gap)))}"`
  ];

  if (tone) {
    attributes.push(`data-wf-tone="${escapeNativeAttribute(tone)}"`);
  }

  return `<div ${attributes.join(' ')}>${children}</div>`;
};

interface NativeControlOptions {
  kind: 'text' | 'select' | 'range';
  settingPath: WaterfallNativeSettingPath;
  label: string;
  caption: string;
  stringValue?: string;
  numberValue?: number;
  placeholder?: string;
  min?: number;
  max?: number;
  step?: number;
  options?: Array<{ value: string; label: string }>;
  tone?: string;
  surface?: string;
}

const buildNativeControl = ({
  kind,
  settingPath,
  label,
  caption,
  stringValue,
  numberValue,
  placeholder,
  min,
  max,
  step,
  options = [],
  tone = 'signal',
  surface = 'control'
}: NativeControlOptions) => {
  const attributes = [
    `data-wf-surface="${escapeNativeAttribute(surface)}"`,
    `data-wf-control="${escapeNativeAttribute(kind)}"`,
    `data-wf-setting="${escapeNativeAttribute(settingPath)}"`,
    `data-wf-label="${escapeNativeAttribute(label)}"`,
    `data-wf-caption="${escapeNativeAttribute(caption)}"`,
    `data-wf-tone="${escapeNativeAttribute(tone)}"`
  ];

  if (typeof stringValue === 'string') {
    attributes.push(`data-wf-value="${escapeNativeAttribute(stringValue)}"`);
  }

  if (typeof numberValue === 'number') {
    attributes.push(`data-wf-value="${numberValue}"`);
  }

  if (placeholder) {
    attributes.push(`data-wf-placeholder="${escapeNativeAttribute(placeholder)}"`);
  }

  if (typeof min === 'number') {
    attributes.push(`data-wf-min="${min}"`);
  }

  if (typeof max === 'number') {
    attributes.push(`data-wf-max="${max}"`);
  }

  if (typeof step === 'number') {
    attributes.push(`data-wf-step="${step}"`);
  }

  if (options.length > 0) {
    attributes.push(
      `data-wf-options="${escapeNativeAttribute(
        options.map((option) => `${option.value}:${option.label}`).join('|')
      )}"`
    );
  }

  return `<wf-control ${attributes.join(' ')} />`;
};

interface WaterfallNativeRouteTimeline {
  entries: string[];
  index: number;
}

interface WaterfallSearchRouteState {
  query: string;
  providerKey: string;
  loading: boolean;
  error: string;
  response: WaterfallSearchResponse | null;
  audit: WaterfallConsigliereAuditResponse | null;
}

const seedNativeRouteTimelines = (tabs: WaterfallTabState[]) =>
  tabs.reduce<Record<string, WaterfallNativeRouteTimeline>>((accumulator, tab) => {
    if (!isWaterfallRoute(tab.url)) {
      return accumulator;
    }

    accumulator[tab.id] = {
      entries: [normalizeWaterfallRoute(tab.url)],
      index: 0
    };
    return accumulator;
  }, {});

interface WaterfallTabPaneProps {
  tab: WaterfallTabState;
  active: boolean;
  onNodeChange: (tabId: string, node: Electron.WebviewTag | null) => void;
  onTabChange: (tabId: string, patch: Partial<WaterfallTabState>) => void;
  onHistoryEntry: (entry: WaterfallHistoryEntry) => void;
}

const createId = (prefix: string) =>
  `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 10)}`;

const getDefaultCollectiveSettings = (): CollectiveContributionSettings => ({
  enabled: false,
  cpuEnabled: true,
  gpuEnabled: false,
  cpuLimitPercent: 25,
  gpuLimitPercent: 20,
  requireIdle: true,
  requireAC: true,
  sessionCapMinutes: 45
});

const getDefaultSecurityWorkbenchSettings = () => ({
  scanDownloadsOnStart: true,
  scanDownloadsOnCompletion: true,
  quarantineHighRiskDownloads: true,
  strictScopeMode: true,
  nativeArtifactScanning: true,
  externalAuthorizedScanning: false,
  exportEvidenceBundles: true
});

const getDefaultSettings = (): WaterfallBrowserSettings => ({
  homePage: WATERFALL_SEARCH_ROUTE,
  searchEngine: 'duckduckgo',
  restoreSession: true,
  collective: getDefaultCollectiveSettings(),
  privacy: {
    doNotTrack: true,
    globalPrivacyControl: true,
    blockTrackers: true,
    httpsOnlyMode: true,
    masterKillSwitch: false,
    permissionsLockdown: true,
    stripReferrers: true,
    antiFingerprinting: true,
    blockPopups: true,
    clearDataOnExit: false,
    blockedHosts: [
      'doubleclick.net',
      'googletagmanager.com',
      'google-analytics.com',
      'facebook.net',
      'adsystem.com'
    ]
  },
  network: {
    proxyMode: 'system',
    proxyRules: '',
    proxyBypassRules: '<local>'
  },
  security: getDefaultSecurityWorkbenchSettings(),
  account: {
    displayName: 'WaterFall Navigator',
    deviceName:
      typeof navigator !== 'undefined' ? navigator.platform || 'Desktop Shell' : 'Desktop Shell',
    nodeId: createId('wf-node'),
    profileVersion: '1.0'
  },
  mesh: {
    protocolVersion: 'wf-mesh-1',
    trustMode: 'invite-only',
    peers: []
  }
});

const getUrlLabel = (targetUrl: string) => {
  if (!targetUrl) {
    return 'New WaterFall Tab';
  }

  try {
    const parsedUrl = new URL(targetUrl);
    if (parsedUrl.protocol === 'waterfall:') {
      if (parsedUrl.hostname.toLowerCase() === 'search') {
        const searchQuery = parsedUrl.searchParams.get('q')?.trim();
        return searchQuery ? `Search | ${searchQuery}` : 'WaterFall Search';
      }

      const routeLabel = parsedUrl.hostname
        .split('-')
        .filter(Boolean)
        .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
        .join(' ');
      return routeLabel ? `WaterFall ${routeLabel}` : 'WaterFall Route';
    }

    return parsedUrl.hostname.replace(/^www\./, '') || parsedUrl.href;
  } catch {
    return targetUrl;
  }
};

const createBlankTab = (): WaterfallTabState => ({
  id: createId('waterfall-tab'),
  title: 'WaterFall Launch Pad',
  url: '',
  loading: false,
  canGoBack: false,
  canGoForward: false,
  lastVisitedAt: Date.now()
});

const createDefaultSession = (): WaterfallBrowserSession => {
  const tab = createBlankTab();
  return {
    tabs: [tab],
    activeTabId: tab.id,
    bookmarks: [],
    history: []
  };
};

const sanitizeSettings = (storedSettings?: Partial<WaterfallBrowserSettings>) => {
  const defaults = getDefaultSettings();
  return {
    ...defaults,
    ...storedSettings,
    collective: {
      ...defaults.collective,
      ...(storedSettings?.collective || {})
    },
    privacy: {
      ...defaults.privacy,
      ...(storedSettings?.privacy || {})
    },
    network: {
      ...defaults.network,
      ...(storedSettings?.network || {})
    },
    security: {
      ...defaults.security,
      ...(storedSettings?.security || {})
    },
    account: {
      ...defaults.account,
      ...(storedSettings?.account || {})
    },
    mesh: {
      ...defaults.mesh,
      ...(storedSettings?.mesh || {}),
      peers: storedSettings?.mesh?.peers || defaults.mesh.peers
    }
  } satisfies WaterfallBrowserSettings;
};

const sanitizeSession = (storedSession?: Partial<WaterfallBrowserSession>) => {
  const defaults = createDefaultSession();
  const tabs =
    storedSession?.tabs && storedSession.tabs.length > 0
      ? storedSession.tabs.map((tab) => ({
          ...createBlankTab(),
          ...tab,
          title: tab.title || getUrlLabel(tab.url || '')
        }))
      : defaults.tabs;
  const activeTabId =
    storedSession?.activeTabId && tabs.some((tab) => tab.id === storedSession.activeTabId)
      ? storedSession.activeTabId
      : tabs[0].id;

  return {
    tabs,
    activeTabId,
    bookmarks: storedSession?.bookmarks || [],
    history: storedSession?.history || []
  } satisfies WaterfallBrowserSession;
};

const isLikelyLocalAddress = (value: string) =>
  /^(localhost|127(?:\.\d{1,3}){3}|10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2})/i.test(value);

const isLikelyDirectBrowserTarget = (value: string) =>
  isLikelyLocalAddress(value) ||
  /^(?:[a-z0-9-]+\.)+[a-z]{2,63}(?::\d{2,5})?(?:[/?#].*)?$/i.test(value) ||
  /^[a-z0-9-]+:\d{2,5}(?:[/?#].*)?$/i.test(value);

const normalizeBrowserTarget = (rawValue: string, _searchEngine: WaterfallSearchEngine) => {
  const trimmedValue = rawValue.trim();

  if (!trimmedValue) {
    return '';
  }

  if (/^[a-zA-Z][a-zA-Z\d+\-.]*:/.test(trimmedValue)) {
    try {
      const parsedUrl = new URL(trimmedValue);
      return parsedUrl.protocol === 'http:' ||
        parsedUrl.protocol === 'https:' ||
        parsedUrl.protocol === 'waterfall:'
        ? parsedUrl.toString()
        : '';
    } catch {
      return '';
    }
  }

  if (trimmedValue.includes(' ')) {
    return buildWaterfallSearchRoute(trimmedValue);
  }

  if (!isLikelyDirectBrowserTarget(trimmedValue)) {
    return buildWaterfallSearchRoute(trimmedValue);
  }

  try {
    const protocol =
      isLikelyLocalAddress(trimmedValue) || /^[a-z0-9-]+:\d{2,5}(?:[/?#].*)?$/i.test(trimmedValue)
        ? 'http://'
        : 'https://';
    return new URL(`${protocol}${trimmedValue}`).toString();
  } catch {
    return buildWaterfallSearchRoute(trimmedValue);
  }
};

const normalizeHomePageTarget = (rawValue: string, searchEngine: WaterfallSearchEngine) => {
  const trimmedValue = rawValue.trim();

  if (!trimmedValue || trimmedValue.includes(' ')) {
    return '';
  }

  return normalizeBrowserTarget(trimmedValue, searchEngine);
};

const dedupeHistory = (entries: WaterfallHistoryEntry[]) => {
  const seen = new Set<string>();
  return entries.filter((entry) => {
    if (seen.has(entry.url)) {
      return false;
    }

    seen.add(entry.url);
    return true;
  });
};

const formatVisitedAt = (timestamp: number) =>
  new Intl.DateTimeFormat(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  }).format(timestamp);

const WaterfallTabPane: React.FC<WaterfallTabPaneProps> = ({
  tab,
  active,
  onNodeChange,
  onTabChange,
  onHistoryEntry
}) => {
  const webviewRef = useRef<Electron.WebviewTag | null>(null);

  useEffect(() => {
    onNodeChange(tab.id, webviewRef.current);
    return () => onNodeChange(tab.id, null);
  }, [onNodeChange, tab.id]);

  useEffect(() => {
    const node = webviewRef.current;
    if (!node || isWaterfallRoute(tab.url)) {
      return;
    }

    const syncState = () => {
      const nextUrl = node.getURL() || tab.url;
      onTabChange(tab.id, {
        url: nextUrl,
        title: node.getTitle() || tab.title || getUrlLabel(nextUrl),
        canGoBack: node.canGoBack(),
        canGoForward: node.canGoForward(),
        loading: typeof node.isLoading === 'function' ? node.isLoading() : false,
        lastVisitedAt: Date.now()
      });
    };

    const handleLoadingStart = () => {
      onTabChange(tab.id, {
        loading: true
      });
    };

    const handleNavigation = () => {
      const nextUrl = node.getURL() || tab.url;
      syncState();

      if (!nextUrl) {
        return;
      }

      onHistoryEntry({
        id: createId('history'),
        title: node.getTitle() || tab.title || getUrlLabel(nextUrl),
        url: nextUrl,
        visitedAt: Date.now()
      });
    };

    const handleTitleUpdate = (event: Event) => {
      const nextTitle = (event as Event & { title?: string }).title;
      if (nextTitle) {
        onTabChange(tab.id, {
          title: nextTitle
        });
      }
    };

    node.addEventListener('did-start-loading', handleLoadingStart as EventListener);
    node.addEventListener('did-stop-loading', syncState as EventListener);
    node.addEventListener('did-finish-load', syncState as EventListener);
    node.addEventListener('did-navigate', handleNavigation as EventListener);
    node.addEventListener('did-navigate-in-page', handleNavigation as EventListener);
    node.addEventListener('page-title-updated', handleTitleUpdate as EventListener);

    syncState();

    return () => {
      node.removeEventListener('did-start-loading', handleLoadingStart as EventListener);
      node.removeEventListener('did-stop-loading', syncState as EventListener);
      node.removeEventListener('did-finish-load', syncState as EventListener);
      node.removeEventListener('did-navigate', handleNavigation as EventListener);
      node.removeEventListener('did-navigate-in-page', handleNavigation as EventListener);
      node.removeEventListener('page-title-updated', handleTitleUpdate as EventListener);
    };
  }, [onHistoryEntry, onTabChange, tab.id, tab.title, tab.url]);

  useEffect(() => {
    const node = webviewRef.current;
    if (!node || !tab.url || isWaterfallRoute(tab.url)) {
      return;
    }

    const currentUrl = node.getURL();
    if (currentUrl !== tab.url) {
      void node.loadURL(tab.url);
    }
  }, [tab.url]);

  if (!tab.url || isWaterfallRoute(tab.url)) {
    return null;
  }

  return (
    <webview
      ref={(node) => {
        webviewRef.current = node as Electron.WebviewTag | null;
      }}
      partition={WATERFALL_PARTITION}
      src={tab.url}
      webpreferences="contextIsolation=yes,sandbox=yes"
      style={{
        display: active ? 'flex' : 'none',
        width: '100%',
        height: '100%',
        border: 'none'
      }}
    />
  );
};

const WaterfallBrowser: React.FC = () => {
  const [bootstrapped, setBootstrapped] = useState(false);
  const [browserNotice, setBrowserNotice] = useState('');
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [settings, setSettings] = useState<WaterfallBrowserSettings>(getDefaultSettings());
  const [resourceProfile, setResourceProfile] = useState<WaterfallResourceProfile | null>(null);
  const [tabs, setTabs] = useState<WaterfallTabState[]>(() => createDefaultSession().tabs);
  const [activeTabId, setActiveTabId] = useState(() => createDefaultSession().activeTabId);
  const [bookmarks, setBookmarks] = useState<WaterfallBookmark[]>([]);
  const [history, setHistory] = useState<WaterfallHistoryEntry[]>([]);
  const [downloads, setDownloads] = useState<WaterfallDownloadRecord[]>([]);
  const [extensions, setExtensions] = useState<WaterfallExtensionRecord[]>([]);
  const [securityStatus, setSecurityStatus] = useState<WaterfallSecurityStatus | null>(null);
  const [securityStatusLoading, setSecurityStatusLoading] = useState(false);
  const [securityStatusError, setSecurityStatusError] = useState('');
  const [bridgeHealth, setBridgeHealth] = useState<WaterfallBridgeHealth | null>(null);
  const [bridgeHealthLoading, setBridgeHealthLoading] = useState(false);
  const [bridgeHealthError, setBridgeHealthError] = useState('');
  const [securityToolkitInventory, setSecurityToolkitInventory] =
    useState<WaterfallSecurityToolkitInventory | null>(null);
  const [securityToolkitLoading, setSecurityToolkitLoading] = useState(false);
  const [securityToolkitError, setSecurityToolkitError] = useState('');
  const [siteShieldTargetUrl, setSiteShieldTargetUrl] = useState('');
  const [updateManifest, setUpdateManifest] = useState<WaterfallUpdateManifest | null>(null);
  const [updatesLoading, setUpdatesLoading] = useState(false);
  const [updateError, setUpdateError] = useState('');
  const [addressDraft, setAddressDraft] = useState('');
  const [settingsHomeDraft, setSettingsHomeDraft] = useState(getDefaultSettings().homePage);
  const [addressFocused, setAddressFocused] = useState(false);
  const [nativeReloadTokens, setNativeReloadTokens] = useState<Record<string, number>>({});
  const [nativeRouteTimelines, setNativeRouteTimelines] = useState<
    Record<string, WaterfallNativeRouteTimeline>
  >(() => seedNativeRouteTimelines(createDefaultSession().tabs));
  const [searchRouteStates, setSearchRouteStates] = useState<
    Record<string, WaterfallSearchRouteState>
  >({});
  const addressInputRef = useRef<HTMLInputElement | null>(null);
  const webviewNodes = useRef<Record<string, Electron.WebviewTag | null>>({});

  const activeTab = useMemo(
    () => tabs.find((tab) => tab.id === activeTabId) ?? tabs[0] ?? createBlankTab(),
    [activeTabId, tabs]
  );
  const activeTabIsInternalRoute = isWaterfallRoute(activeTab.url);
  const activeWebview = activeTabId ? webviewNodes.current[activeTabId] : null;
  const bookmarked = Boolean(activeTab.url && bookmarks.some((bookmark) => bookmark.url === activeTab.url));
  const updateManifestReady = Boolean(
    updateManifest && updateManifest.available && updateManifest.integrityState === 'verified'
  );
  const securitySummary = useMemo(
    () =>
      downloads.reduce(
        (accumulator, download) => {
          accumulator.totalDownloads += 1;
          const verdict = download.securityScan?.verdict;

          if (verdict === 'clean') {
            accumulator.clean += 1;
          } else if (verdict === 'review') {
            accumulator.review += 1;
          } else if (verdict === 'quarantined') {
            accumulator.quarantined += 1;
          } else {
            accumulator.pending += 1;
          }

          return accumulator;
        },
        {
          totalDownloads: 0,
          clean: 0,
          review: 0,
          quarantined: 0,
          pending: 0
        }
      ),
    [downloads]
  );
  const collectiveProjection = useMemo(() => {
    if (!resourceProfile) {
      return {
        localUnits: 0,
        projections: [] as Array<{ participants: number; units: number }>
      };
    }

    const cpuUnits = settings.collective.cpuEnabled
      ? resourceProfile.cpu.cores * (settings.collective.cpuLimitPercent / 100) * 12
      : 0;
    const gpuDevices = resourceProfile.gpu.activeDeviceCount || resourceProfile.gpu.devices.length;
    const gpuUnits = settings.collective.gpuEnabled
      ? gpuDevices * (settings.collective.gpuLimitPercent / 100) * 48
      : 0;
    const localUnits = Number((cpuUnits + gpuUnits).toFixed(1));

    return {
      localUnits,
      projections: [8, 64, 512].map((participants) => ({
        participants,
        units: Number((localUnits * participants).toFixed(1))
      }))
    };
  }, [resourceProfile, settings.collective]);
  const privacyPosture = useMemo(() => {
    const protections = [
      settings.privacy.doNotTrack,
      settings.privacy.globalPrivacyControl,
      settings.privacy.blockTrackers,
      settings.privacy.httpsOnlyMode,
      settings.privacy.masterKillSwitch,
      settings.privacy.permissionsLockdown,
      settings.privacy.stripReferrers,
      settings.privacy.antiFingerprinting,
      settings.privacy.blockPopups,
      settings.security.scanDownloadsOnStart,
      settings.security.scanDownloadsOnCompletion,
      settings.security.quarantineHighRiskDownloads
    ];
    const enabled = protections.filter(Boolean).length;
    const total = protections.length;

    return {
      enabled,
      total,
      score: Math.round((enabled / total) * 100)
    };
  }, [settings]);

  const refreshUpdateManifest = useCallback(
    async (quiet = false) => {
      if (!window.waterfall?.updates) {
        return null;
      }

      setUpdatesLoading(true);
      if (!quiet) {
        setUpdateError('');
      }

      try {
        const nextManifest = await window.waterfall.updates.check();
        setUpdateManifest(nextManifest);
        setUpdateError('');
        return nextManifest;
      } catch (error) {
        const message =
          error instanceof Error ? error.message : 'WaterFall could not verify the update manifest.';
        setUpdateError(message);
        if (!quiet) {
          setBrowserNotice(message);
        }
        return null;
      } finally {
        setUpdatesLoading(false);
      }
    },
    []
  );
  const refreshSecurityStatus = useCallback(
    async (quiet = false) => {
      if (!window.waterfall?.security) {
        return null;
      }

      setSecurityStatusLoading(true);
      if (!quiet) {
        setSecurityStatusError('');
      }

      try {
        const nextStatus = await window.waterfall.security.getStatus();
        setSecurityStatus(nextStatus);
        setSecurityStatusError('');
        return nextStatus;
      } catch (error) {
        const message =
          error instanceof Error ? error.message : 'WaterFall could not refresh security status.';
        setSecurityStatusError(message);
        if (!quiet) {
          setBrowserNotice(message);
        }
        return null;
      } finally {
        setSecurityStatusLoading(false);
      }
    },
    []
  );
  const refreshBridgeHealth = useCallback(
    async (quiet = false) => {
      if (!window.waterfall?.orchestrator) {
        return null;
      }

      setBridgeHealthLoading(true);
      if (!quiet) {
        setBridgeHealthError('');
      }

      try {
        const nextHealth = await window.waterfall.orchestrator.getBridgeHealth();
        setBridgeHealth(nextHealth);
        setBridgeHealthError('');
        return nextHealth;
      } catch (error) {
        const message =
          error instanceof Error ? error.message : 'WaterFall could not refresh bridge health.';
        setBridgeHealthError(message);
        if (!quiet) {
          setBrowserNotice(message);
        }
        return null;
      } finally {
        setBridgeHealthLoading(false);
      }
    },
    []
  );
  const refreshSecurityToolkitInventory = useCallback(
    async (quiet = false) => {
      if (!window.electron?.browser) {
        return null;
      }

      setSecurityToolkitLoading(true);
      if (!quiet) {
        setSecurityToolkitError('');
      }

      try {
        const nextInventory = await window.electron.browser.getSecurityToolkitInventory();
        setSecurityToolkitInventory(nextInventory);
        setSecurityToolkitError('');
        return nextInventory;
      } catch (error) {
        const message =
          error instanceof Error
            ? error.message
            : 'WaterFall could not refresh the Security Architect toolkit inventory.';
        setSecurityToolkitError(message);
        if (!quiet) {
          setBrowserNotice(message);
        }
        return null;
      } finally {
        setSecurityToolkitLoading(false);
      }
    },
    []
  );
  const activeSearchRouteKey =
    activeTabIsInternalRoute && isWaterfallSearchRoute(activeTab.url)
      ? normalizeWaterfallRoute(activeTab.url)
      : '';
  const activeSearchQuery = activeSearchRouteKey ? getWaterfallSearchQuery(activeTab.url) : '';
  const activeSearchReloadToken = nativeReloadTokens[activeTab.id] || 0;

  useEffect(() => {
    if (!activeSearchRouteKey || !window.waterfall?.search) {
      return;
    }

    const orderedProviders = getOrderedSearchProviders(settings.searchEngine);
    const providerKey = orderedProviders.join('|');

    if (!activeSearchQuery) {
      setSearchRouteStates((current) => ({
        ...current,
        [activeSearchRouteKey]: {
          query: '',
          providerKey,
          loading: false,
          error: '',
          response: null,
          audit: null
        }
      }));
      return;
    }

    let cancelled = false;
    setSearchRouteStates((current) => ({
      ...current,
      [activeSearchRouteKey]: {
        query: activeSearchQuery,
        providerKey,
        loading: true,
        error: '',
        response: current[activeSearchRouteKey]?.response || null,
        audit: current[activeSearchRouteKey]?.audit || null
      }
    }));

    const searchPayload: WaterfallSearchQuery = {
      query: activeSearchQuery,
      regionBias: 'auto',
      safeSearch: true,
      recencyBiasHours: 0,
      providers: orderedProviders
    };

    const runSearch = async () => {
      try {
        const cachedResponse = await window.waterfall!.search.getCachedResults(searchPayload);
        const response = cachedResponse || (await window.waterfall!.search.query(searchPayload));
        let audit: WaterfallConsigliereAuditResponse | null = null;

        if (response.results.length > 0) {
          try {
            const auditRequest: WaterfallConsigliereAuditRequest = {
              query: searchPayload,
              rawResults: response.results
            };
            audit = await window.waterfall!.search.audit(auditRequest);
          } catch {
            audit = null;
          }
        }

        if (window.waterfall?.ledger?.recordEvent) {
          void window.waterfall.ledger.recordEvent({
            type: 'native-search-executed',
            summary: 'WaterFall executed a native search query.',
            target: WATERFALL_SEARCH_ROUTE,
            timestamp: Date.now(),
            metadata: {
              cacheMode: cachedResponse ? 'private-cache' : 'bridge',
              providerCount: String(orderedProviders.length),
              queryLength: String(activeSearchQuery.length),
              route: activeSearchRouteKey
            }
          });
        }

        if (cancelled) {
          return;
        }

        setSearchRouteStates((current) => ({
          ...current,
          [activeSearchRouteKey]: {
            query: activeSearchQuery,
            providerKey,
            loading: false,
            error: '',
            response,
            audit
          }
        }));
      } catch (error) {
        if (cancelled) {
          return;
        }

        setSearchRouteStates((current) => ({
          ...current,
          [activeSearchRouteKey]: {
            query: activeSearchQuery,
            providerKey,
            loading: false,
            error:
              error instanceof Error
                ? error.message
                : 'WaterFall search could not complete that query.',
            response: null,
            audit: null
          }
        }));
      }
    };

    void runSearch();

    return () => {
      cancelled = true;
    };
  }, [activeSearchQuery, activeSearchReloadToken, activeSearchRouteKey, settings.searchEngine]);
  const nativeDocumentsByRoute = useMemo(() => {
    const documents: Record<string, WaterfallNativeDocument> = {};
    const availableRoutes = [
      {
        route: 'waterfall://home',
        title: 'Native Home',
        body: 'Return to WaterFall’s first-party dashboard.',
        tone: 'lagoon'
      },
      {
        route: 'waterfall://search',
        title: 'Search Deck',
        body: 'Run native sovereign search with transparent provider lanes.',
        tone: 'lagoon'
      },
      {
        route: 'waterfall://engine-lab',
        title: 'Engine Lab',
        body: 'Inspect the native renderer lane and roadmap.',
        tone: 'ember'
      },
      {
        route: 'waterfall://history',
        title: 'History Deck',
        body: 'See where this browser session has been.',
        tone: 'signal'
      },
      {
        route: 'waterfall://bookmarks',
        title: 'Bookmark Deck',
        body: 'Open the pinned routes WaterFall is holding onto.',
        tone: 'signal'
      },
      {
        route: 'waterfall://downloads',
        title: 'Download Hangar',
        body: 'Inspect local payload progress and reveal files.',
        tone: 'signal'
      },
      {
        route: WATERFALL_SECURITY_WORKBENCH_ROUTE,
        title: 'Security Workbench',
        body: 'Run download scans, inspect quarantine posture, and export evidence.',
        tone: 'ember'
      },
      {
        route: WATERFALL_SITE_SHIELD_ROUTE,
        title: 'Site Shield',
        body: 'Inspect the active route, browser guardrails, and protection posture.',
        tone: 'signal'
      },
      {
        route: WATERFALL_PRIVACY_AUDITOR_ROUTE,
        title: 'Privacy Auditor',
        body: 'Review bridge health, privacy posture, and the current exposure surface.',
        tone: 'lagoon'
      },
      {
        route: WATERFALL_SECURITY_ARCHITECT_ROUTE,
        title: 'Security Architect',
        body: 'Inspect the authorized toolkit inventory and export bounty-ready evidence packs.',
        tone: 'ember'
      },
      {
        route: WATERFALL_UPDATES_ROUTE,
        title: 'Update Deck',
        body: 'Inspect signed release manifests, staged artifacts, and rollback posture.',
        tone: 'ember'
      },
      {
        route: 'waterfall://settings',
        title: 'Settings Snapshot',
        body: 'Inspect identity, privacy, and collective posture.',
        tone: 'lagoon'
      },
      {
        route: 'waterfall://session',
        title: 'Session Deck',
        body: 'View open tabs and active session memory.',
        tone: 'signal'
      },
      {
        route: 'waterfall://extensions',
        title: 'Extension Deck',
        body: 'Manage trusted unpacked extensions.',
        tone: 'ember'
      },
      {
        route: 'waterfall://collective',
        title: 'Collective Deck',
        body: 'Review the voluntary shared-compute posture.',
        tone: 'ember'
      },
      {
        route: 'waterfall://mesh',
        title: 'Mesh Deck',
        body: 'Inspect trust posture and node identity.',
        tone: 'lagoon'
      },
      {
        route: 'waterfall://routes',
        title: 'Route Atlas',
        body: 'Survey every native page that is currently live.',
        tone: 'signal'
      },
      {
        route: 'waterfall://orchestrator',
        title: 'Orchestrator Deck',
        body: 'Inspect the privacy-first architecture and system map for WaterFall.',
        tone: 'lagoon'
      },
      {
        route: 'waterfall://privacy-fortress',
        title: 'Privacy Fortress',
        body: 'Review the browser use cases, privacy posture, and protection targets.',
        tone: 'ember'
      },
      {
        route: 'waterfall://security-proof',
        title: 'Security Proof',
        body: 'Inspect security architecture, tests, examples, and implementation evidence.',
        tone: 'signal'
      }
    ];

    const siteShieldInspectionTarget =
      normalizeWaterfallRoute(activeTab.url) === WATERFALL_SITE_SHIELD_ROUTE && siteShieldTargetUrl
        ? siteShieldTargetUrl
        : activeTab.url;

    const activeRouteSummary = (() => {
      if (!siteShieldInspectionTarget) {
        return {
          host: 'no-route',
          protocol: 'idle',
          displayUrl: 'No active route is selected yet.',
          lane: 'idle'
        };
      }

      if (isWaterfallRoute(siteShieldInspectionTarget)) {
        return {
          host: 'waterfall-native',
          protocol: 'waterfall:',
          displayUrl: siteShieldInspectionTarget,
          lane: 'native'
        };
      }

      try {
        const parsedUrl = new URL(siteShieldInspectionTarget);
        return {
          host: parsedUrl.hostname,
          protocol: parsedUrl.protocol,
          displayUrl: siteShieldInspectionTarget,
          lane: parsedUrl.protocol === 'https:' ? 'secure-web' : 'web'
        };
      } catch {
        return {
          host: 'unknown',
          protocol: 'unknown',
          displayUrl: siteShieldInspectionTarget,
          lane: 'unknown'
        };
      }
    })();
    const toolkitCategoryCards =
      securityToolkitInventory && securityToolkitInventory.categories.length > 0
        ? securityToolkitInventory.categories
            .map((category) =>
              buildNativeCard({
                title: category.name,
                body: `${category.toolCount} visible entries | ${category.sampleEntries.join(' | ') || 'no sample entries'}`,
                tone: 'ember'
              })
            )
            .join('')
        : buildNativeCard({
            title: securityToolkitLoading ? 'Scanning Toolkit Inventory' : 'Toolkit Inventory Pending',
            body:
              securityToolkitError ||
              'WaterFall has not surfaced the Security Architect toolkit inventory yet.',
            tone: 'signal'
          });

    const machineCards = resourceProfile
      ? [
          buildNativeCard({
            title: 'CPU Spine',
            body: `${resourceProfile.cpu.model} | ${resourceProfile.cpu.cores} cores | ${resourceProfile.cpu.speedMhz} MHz`,
            tone: 'lagoon'
          }),
          buildNativeCard({
            title: 'Memory Pool',
            body: `${resourceProfile.memory.totalGb} GB total | ${resourceProfile.memory.freeGb} GB free`,
            tone: 'signal'
          }),
          buildNativeCard({
            title: 'GPU Lane',
            body: resourceProfile.gpu.devices.length
              ? `${resourceProfile.gpu.devices.length} device(s) surfaced | ${resourceProfile.gpu.activeDeviceCount} active`
              : 'No GPU device surfaced by Electron yet.',
            tone: 'ember'
          })
        ].join('')
      : buildNativeCard({
          title: 'Machine Profile Pending',
          body: 'WaterFall has not surfaced a local resource profile yet.',
          tone: 'ember'
        });

    const historyCards =
      history.length > 0
        ? history
            .slice(0, 10)
            .map((entry) =>
              buildNativeCard({
                title: entry.title,
                body: `${entry.url} | ${formatVisitedAt(entry.visitedAt)}`,
                href: entry.url,
                tone: 'signal'
              })
            )
            .join('')
        : buildNativeCard({
            title: 'No Route Memory Yet',
            body: 'Take WaterFall somewhere and this deck will begin filling in.',
            href: 'waterfall://home',
            tone: 'ember'
          });

    const bookmarkCards =
      bookmarks.length > 0
        ? bookmarks
            .slice(0, 10)
            .map((bookmark) =>
              buildNativeCard({
                title: bookmark.title,
                body: bookmark.url,
                href: bookmark.url,
                tone: 'lagoon'
              })
            )
            .join('')
        : buildNativeCard({
            title: 'No Bookmarks Yet',
            body: 'Pin routes from the main browser shell and they will appear here.',
            href: 'waterfall://home',
            tone: 'ember'
          });

    const downloadCards =
      downloads.length > 0
        ? downloads
            .slice(0, 10)
            .map((download, index) =>
              buildNativeCard({
                title: download.filename,
                body: `${download.status} | ${formatKilobytes(download.receivedBytes)} of ${formatKilobytes(download.totalBytes)}${download.securityScan ? ` | ${download.securityScan.verdict} | risk ${download.securityScan.riskScore}` : ''}`,
                actionId: `download-${index}`,
                tone: 'signal'
              })
            )
            .join('')
        : buildNativeCard({
            title: 'No Payloads Yet',
            body: 'Downloads will land here once WaterFall catches them.',
            href: 'waterfall://home',
            tone: 'ember'
          });

    const sessionCards =
      tabs.length > 0
        ? tabs
            .slice(0, 10)
            .map((tab) => {
              const target = tab.url || 'waterfall://home';
              return buildNativeCard({
                title: `${tab.id === activeTabId ? 'Active' : 'Standby'} | ${tab.title}`,
                body: target,
                href: target,
                tone: tab.id === activeTabId ? 'lagoon' : 'signal'
              });
            })
            .join('')
        : buildNativeCard({
            title: 'No Live Tabs',
            body: 'Resetting the session will rebuild the launch pad.',
            actionId: 'reset-session',
            tone: 'ember'
          });

    const extensionCards =
      extensions.length > 0
        ? extensions
            .slice(0, 10)
            .map((extension, index) =>
              buildNativeCard({
                title: extension.name,
                body: extension.loadError || `${extension.version || 'unversioned'} | ${extension.path}`,
                actionId: `extension-${index}`,
                tone: extension.loadError ? 'ember' : 'signal'
              })
            )
            .join('')
        : buildNativeCard({
            title: 'No Extensions Loaded',
            body: 'Trusted unpacked extensions can be added from the settings drawer.',
            actionId: 'open-extension-settings',
            tone: 'ember'
          });
    const securityWorkbenchCards =
      downloads.length > 0
        ? downloads
            .slice(0, 10)
            .map((download) =>
              buildNativeCard({
                title: download.filename,
                body: download.securityScan
                  ? `${download.securityScan.stage} | ${download.securityScan.verdict} | risk ${download.securityScan.riskScore} | ${download.securityScan.findings.join(' | ') || 'no findings'}`
                  : `No scan state yet | ${download.status} | ${download.mimeType || 'unknown mime'}`,
                actionId: download.securityScan?.quarantined
                  ? `release-quarantine-${download.id}`
                  : `scan-download-${download.id}`,
                tone: download.securityScan?.quarantined
                  ? 'ember'
                  : download.securityScan?.verdict === 'review'
                    ? 'signal'
                    : 'lagoon'
              })
            )
            .join('')
        : buildNativeCard({
            title: 'No Download Artifacts',
            body: 'WaterFall will surface scanned payloads here once downloads begin flowing.',
            href: 'waterfall://downloads',
            tone: 'signal'
          });

    const updateStatusTone = updateError
      ? 'ember'
      : updatesLoading
        ? 'signal'
        : updateManifest?.integrityState === 'verified'
          ? 'lagoon'
          : updateManifest?.integrityState === 'unverified'
            ? 'ember'
            : 'signal';
    const updateSummaryCards = updateManifest
      ? [
          buildNativeCard({
            title: updateManifest.available
              ? `Update ${updateManifest.version} Ready`
              : `Current Build ${updateManifest.version}`,
            body:
              updateManifest.statusMessage ||
              'WaterFall is holding the latest known updater state.',
            tone: updateStatusTone
          }),
          buildNativeCard({
            title: 'Integrity Posture',
            body: `Manifest ${updateManifest.integrityState} | Channel ${updateManifest.channel} | Stage ${updateManifest.stageStatus || 'idle'} | Rollback ${updateManifest.rollbackReady ? 'ready' : 'not staged'}`,
            tone:
              updateManifest.integrityState === 'verified'
                ? 'lagoon'
                : updateManifest.integrityState === 'unverified'
                  ? 'ember'
                  : 'signal'
          }),
          buildNativeCard({
            title: 'Artifact Fingerprint',
            body: updateManifest.artifactSha256
              ? `${updateManifest.artifactName || 'artifact'} | sha256 ${updateManifest.artifactSha256}`
              : 'WaterFall has not been given an artifact fingerprint yet.',
            tone: 'signal'
          })
        ].join('')
      : buildNativeCard({
          title: 'Update Status Pending',
          body: updatesLoading
            ? 'WaterFall is checking the signed updater lane.'
            : updateError || 'WaterFall has not checked the updater lane yet.',
          tone: updateStatusTone
        });
    const updateNoteCards =
      updateManifest && updateManifest.notes.length > 0
        ? updateManifest.notes
            .map((note, index) =>
              buildNativeCard({
                title: `Release Note ${index + 1}`,
                body: note,
                tone: 'signal'
              })
            )
            .join('')
        : buildNativeCard({
            title: 'Release Notes Pending',
            body: 'Visible release notes will appear here once WaterFall receives a signed manifest.',
            tone: 'signal'
          });

    const routeCards = availableRoutes
      .map((route) =>
        buildNativeCard({
          title: route.title,
          body: route.body,
          href: route.route,
          tone: route.tone
        })
      )
      .join('');

    const orchestratorSystemCards = [
      buildNativeCard({
        title: 'Master Orchestrator',
        body: 'Design target: one encrypted control plane coordinating browser, VPN, firewall, ledger, and kill switch behavior.',
        tone: 'lagoon'
      }),
      buildNativeCard({
        title: '8 Firewall Types',
        body: 'Packet filtering, circuit gateway, stateful inspection, proxy, NGFW, software, hardware, and cloud firewall layers are part of the intended stack.',
        tone: 'ember'
      }),
      buildNativeCard({
        title: 'Built-In VPN',
        body: 'Design target: native multi-hop routing, kill switch coverage, DNS leak protection, IPv6 protection, and stealth transports.',
        tone: 'signal'
      }),
      buildNativeCard({
        title: 'Encrypted Browser Plane',
        body: 'Target posture: encrypted queries, encrypted visited-site records, encrypted storage, isolated tabs, anti-tracking, and no telemetry.',
        tone: 'lagoon'
      }),
      buildNativeCard({
        title: 'Privacy Systems',
        body: 'Ledger, anti-tracker, anti-malware, onion routing, DNS-over-HTTPS, and ephemeral storage all belong in the privacy layer.',
        tone: 'signal'
      }),
      buildNativeCard({
        title: 'Security Systems',
        body: 'MFA, DOS trap mode, MicroVM isolation, and hardware root-of-trust protections define the hard security lane.',
        tone: 'ember'
      }),
      buildNativeCard({
        title: 'AI And Media Systems',
        body: 'Consigliere, encrypted media workflows, remote access, and on-device assistance sit above the browser substrate.',
        tone: 'signal'
      }),
      buildNativeCard({
        title: 'Settings System',
        body: 'The browser is trending toward the original 13-category privacy-first control model instead of a generic settings drawer.',
        href: 'waterfall://settings',
        tone: 'lagoon'
      })
    ].join('');

    const privacyUseCaseCards = [
      buildNativeCard({
        title: 'Maximum Privacy Browsing',
        body: 'Target state: encrypted browsing, no telemetry, anti-fingerprinting, and zero-retention session behavior.',
        tone: 'lagoon'
      }),
      buildNativeCard({
        title: 'Secure Research',
        body: 'Search routing, encrypted local state, and hardened privacy controls are intended to protect sensitive exploration.',
        tone: 'signal'
      }),
      buildNativeCard({
        title: 'Anonymous Communication',
        body: 'Design target: multi-hop VPN plus onion routing and transport obfuscation without leaking surrounding network identity.',
        tone: 'ember'
      }),
      buildNativeCard({
        title: 'Threat Protection',
        body: 'The long-term stack pairs firewall orchestration with malware, phishing, and compromise-response layers.',
        tone: 'ember'
      }),
      buildNativeCard({
        title: 'Leak-Proof Browsing',
        body: 'Kill-switch coordination, DNS protection, HTTPS upgrading, and privacy auditing are all part of the browser mission.',
        tone: 'signal'
      }),
      buildNativeCard({
        title: 'No Pop-Ups Or Redirects',
        body: 'Current WaterFall already denies popup windows by default and centers navigation inside the browser shell.',
        tone: 'lagoon'
      }),
      buildNativeCard({
        title: 'Current Operational Lane',
        body: `Live today: DNT ${settings.privacy.doNotTrack ? 'on' : 'off'}, GPC ${settings.privacy.globalPrivacyControl ? 'on' : 'off'}, HTTPS upgrades ${settings.privacy.httpsOnlyMode ? 'on' : 'off'}, tracker blocking ${settings.privacy.blockTrackers ? 'on' : 'off'}, kill switch ${settings.privacy.masterKillSwitch ? 'armed' : 'idle'}, permissions lockdown ${settings.privacy.permissionsLockdown ? 'on' : 'off'}, referrer stripping ${settings.privacy.stripReferrers ? 'on' : 'off'}, anti-fingerprinting ${settings.privacy.antiFingerprinting ? 'on' : 'off'}, popup blocker ${settings.privacy.blockPopups ? 'on' : 'off'}, downloads ${downloads.length}, extensions ${extensions.length}.`,
        tone: 'signal'
      }),
      buildNativeCard({
        title: 'Orchestrator Deck',
        body: 'Open the architecture map that ties the privacy-first browser together.',
        href: 'waterfall://orchestrator',
        tone: 'lagoon'
      })
    ].join('');

    const securityProofCards = [
      buildNativeCard({
        title: 'Enforced In This Build',
        body: `Kill switch ${settings.privacy.masterKillSwitch ? 'armed' : 'idle'} | permissions lockdown ${settings.privacy.permissionsLockdown ? 'on' : 'off'} | referrer stripping ${settings.privacy.stripReferrers ? 'on' : 'off'} | anti-fingerprinting ${settings.privacy.antiFingerprinting ? 'on' : 'off'} | popup blocker ${settings.privacy.blockPopups ? 'on' : 'off'}.`,
        tone: 'lagoon'
      }),
      buildNativeCard({
        title: 'Core Security',
        body: 'End-to-end encryption, zero-knowledge storage intent, forensic resistance, kill switch posture, no-logs policy, anti-fingerprinting, and leak protection define the security baseline.',
        tone: 'lagoon'
      }),
      buildNativeCard({
        title: 'Threat Model',
        body: 'The design expects explicit threat documentation, honest scope boundaries, encryption assumptions, and incident-response procedures instead of vague security marketing.',
        tone: 'ember'
      }),
      buildNativeCard({
        title: 'Secret Management',
        body: 'Secrets belong in environment variables or secure vaults only. No hardcoded credentials, and rotation should remain first-class.',
        tone: 'signal'
      }),
      buildNativeCard({
        title: 'Advanced Security Systems',
        body: 'Hardware root of trust, DOS trap mode, MFA, MicroVM isolation, accountability ledger, and network stealth all belong in the hardened stack.',
        tone: 'ember'
      }),
      buildNativeCard({
        title: 'Example Surface',
        body: 'The design references basic, complete, advanced, MFA, MicroVM, DOS trap, ledger, hardware-root, stealth, and concrete implementation demos.',
        tone: 'signal'
      }),
      buildNativeCard({
        title: 'Test Coverage',
        body: 'VPN handshakes, firewall enforcement, platform detection, fallback, resilience, MFA, MicroVM, DOS trap, privacy ledger, and stealth transports are all called out as required coverage.',
        tone: 'lagoon'
      }),
      buildNativeCard({
        title: 'CI And Proof',
        body: 'Implementation proof lives in backend verification scripts, example flows, comprehensive tests, CI pipelines, and documentation rather than promises alone.',
        tone: 'signal'
      })
    ].join('');

    const searchRoutes = Array.from(
      new Set([
        WATERFALL_SEARCH_ROUTE,
        ...tabs
          .map((tab) => tab.url)
          .filter((route): route is string => Boolean(route) && isWaterfallSearchRoute(route))
          .map((route) => normalizeWaterfallRoute(route))
      ])
    );

    searchRoutes.forEach((route) => {
      const searchQuery = getWaterfallSearchQuery(route);
      const orderedProviders = getOrderedSearchProviders(settings.searchEngine);
      const providerLabels = orderedProviders
        .map((provider) => SEARCH_ENGINE_LABELS[provider])
        .join(' -> ');
      const searchState = searchRouteStates[route];
      const response = searchState?.response;
      const audit = searchState?.audit;
      const resultCards =
        response && response.results.length > 0
          ? response.results
              .map((result) =>
                buildNativeCard({
                  title: result.title,
                  body: `${result.provider} | ${(result.relevanceScore * 100).toFixed(0)}% | ${result.snippet || result.url}${result.categories.length ? ` | ${result.categories.join(', ')}` : ''}`,
                  href: result.url,
                  tone: 'signal'
                })
              )
              .join('')
          : searchQuery && !searchState?.loading && !searchState?.error
            ? buildNativeCard({
                title: 'No Results Returned',
                body: 'WaterFall did not receive any result envelopes for this query yet.',
                tone: 'ember'
              })
            : [
                buildNativeCard({
                  title: 'Search The Sovereign Web',
                  body: 'Type into the address bar and WaterFall will route the query to waterfall://search with native result rendering.',
                  tone: 'lagoon'
                }),
                buildNativeCard({
                  title: 'Try A Browser Query',
                  body: 'Open a native search for WaterFall browser architecture.',
                  href: buildWaterfallSearchRoute('WaterFall browser architecture'),
                  tone: 'signal'
                }),
                buildNativeCard({
                  title: 'Try A Privacy Query',
                  body: 'Open a native search for privacy accountability ledgers.',
                  href: buildWaterfallSearchRoute('privacy accountability ledger'),
                  tone: 'signal'
                }),
                buildNativeCard({
                  title: 'Try An Engine Query',
                  body: 'Open a native search for rendering engine milestones.',
                  href: buildWaterfallSearchRoute('rendering engine milestones'),
                  tone: 'ember'
                })
              ].join('');
      const warningCards =
        response?.warnings && response.warnings.length > 0
          ? response.warnings
              .map((warning) =>
                buildNativeCard({
                  title: 'Search Warning',
                  body: warning,
                  tone: 'ember'
                })
              )
              .join('')
          : buildNativeCard({
              title: 'Transparent Ordering',
              body: 'WaterFall is preserving provider envelopes and only layering an audited Consigliere sidecar on top.',
              tone: 'lagoon'
            });
      const summaryCards =
        audit && Object.keys(audit.optionalSummaries).length > 0
          ? Object.entries(audit.optionalSummaries)
              .map(([provider, summary]) =>
                buildNativeCard({
                  title: `${provider} Summary`,
                  body: summary,
                  tone: 'signal'
                })
              )
              .join('')
          : '';
      const auditCards =
        audit &&
        (audit.privacyFlags.length > 0 ||
          audit.sourceClusters.length > 0 ||
          audit.explanationCards.length > 0 ||
          Boolean(summaryCards))
          ? [
              ...(audit.privacyFlags.length > 0
                ? [
                    buildNativeCard({
                      title: 'Privacy Flags',
                      body: audit.privacyFlags.join(' | '),
                      tone: 'ember'
                    })
                  ]
                : []),
              ...(audit.sourceClusters.length > 0
                ? [
                    buildNativeCard({
                      title: 'Source Clusters',
                      body: audit.sourceClusters.join(' | '),
                      tone: 'signal'
                    })
                  ]
                : []),
              ...audit.explanationCards.map((card, index) =>
                buildNativeCard({
                  title: `Consigliere Note ${index + 1}`,
                  body: card,
                  tone: 'lagoon'
                })
              ),
              summaryCards
            ].join('')
          : buildNativeCard({
              title: 'Consigliere Sidecar',
              body: searchQuery
                ? 'Consigliere annotations will appear here once result envelopes are available.'
                : 'Consigliere joins the search path as a transparent audit lane, not as a hidden reranker.',
              tone: 'signal'
            });

      documents[route] = {
        route,
        title: searchQuery ? `WaterFall Search | ${searchQuery}` : 'WaterFall Search',
        subtitle: searchQuery
          ? `Native search results for "${searchQuery}" with transparent provider lanes.`
          : 'A first-party native search surface for WaterFall.',
        markup: `<main data-wf-surface="hero" data-wf-tone="lagoon"><h1>WaterFall Search</h1><p>WaterFall is rendering search results as a first-party route. Provider lane priority: ${escapeNativeText(providerLabels)}.</p><section><h2>Search Status</h2>${buildNativeCluster({ columns: 3, children: `${buildNativeCard({
          title: searchQuery ? `Query | ${searchQuery}` : 'Search Ready',
          body: searchQuery
            ? searchState?.loading
              ? `WaterFall is querying ${providerLabels}.`
              : searchState?.error
                ? searchState.error
                : `${response?.results.length || 0} result(s) across ${orderedProviders.length} provider lane(s).`
            : 'Use the omnibox or open waterfall://search?q=... directly to populate this deck.',
          tone: searchState?.error ? 'ember' : searchState?.loading ? 'signal' : 'lagoon',
          span: 2,
          emphasis: 'priority'
        })}${buildNativeCard({
          title: 'Lead Search Lane',
          body: SEARCH_ENGINE_LABELS[settings.searchEngine],
          href: 'waterfall://settings',
          tone: 'signal'
        })}${buildNativeCard({
          title: 'Clear Search Deck',
          body: 'Open a blank native search route.',
          href: WATERFALL_SEARCH_ROUTE,
          tone: 'signal'
        })}` })}</section><section><h2>Result Lanes</h2>${buildNativeCluster({ columns: 2, children: resultCards })}</section><section><h2>Consigliere Audit</h2>${buildNativeCluster({ columns: 2, children: auditCards, tone: 'lagoon' })}</section><section><h2>Warnings And Policy</h2>${buildNativeCluster({ columns: 2, children: warningCards, tone: 'ember' })}</section><section><h2>Native Hubs</h2>${buildNativeCluster({ columns: 3, children: `${buildNativeCard({
          title: 'Native Home',
          body: 'Return to the WaterFall dashboard.',
          href: WATERFALL_HOME_ROUTE,
          tone: 'lagoon'
        })}${buildNativeCard({
          title: 'Settings Snapshot',
          body: 'Adjust provider priority and privacy posture.',
          href: 'waterfall://settings',
          tone: 'signal'
        })}${buildNativeCard({
          title: 'Route Atlas',
          body: 'Survey the rest of the native route network.',
          href: 'waterfall://routes',
          tone: 'signal'
        })}` })}</section></main>`
      };
    });

    documents['waterfall://home'] = {
      route: 'waterfall://home',
      title: 'WaterFall Native Home',
      subtitle: 'A live first-party dashboard for this WaterFall session.',
      markup: `<main data-wf-surface="hero" data-wf-tone="lagoon"><h1>WaterFall Native Home</h1><p>Thirsty's WaterFall is rendering its own session dashboard through the native route lane, and these cards can move you through the browser directly.</p><section><h2>Command Deck</h2>${buildNativeCluster({ columns: 3, children: `${buildNativeCard({
        title: 'Session Deck',
        body: `${tabs.length} tab(s) online and ${history.length} recent route memories in reach.`,
        href: 'waterfall://session',
        tone: 'lagoon',
        span: 2,
        emphasis: 'priority'
      })}${buildNativeCard({
        title: 'History Deck',
        body: `${history.length} route entries are ready for replay.`,
        href: 'waterfall://history',
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Bookmark Deck',
        body: `${bookmarks.length} bookmarked route(s) are pinned close at hand.`,
        href: 'waterfall://bookmarks',
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Download Hangar',
        body: `${downloads.length} download record(s) are tracked in this session.`,
        href: 'waterfall://downloads',
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Security Workbench',
        body: `${securitySummary.quarantined} quarantined | ${securitySummary.review} review | ${securitySummary.clean} clean.`,
        href: WATERFALL_SECURITY_WORKBENCH_ROUTE,
        tone: securitySummary.quarantined > 0 ? 'ember' : 'signal'
      })}${buildNativeCard({
        title: 'Site Shield',
        body: `${activeRouteSummary.host} | ${activeRouteSummary.protocol} | ${activeRouteSummary.lane}`,
        href: WATERFALL_SITE_SHIELD_ROUTE,
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Privacy Auditor',
        body: `${privacyPosture.score}% posture | bridge ${bridgeHealth?.mode || 'pending'} | ${securityStatus?.warnings.length || 0} warning(s).`,
        href: WATERFALL_PRIVACY_AUDITOR_ROUTE,
        tone: 'lagoon'
      })}${buildNativeCard({
        title: 'Security Architect',
        body: securityToolkitInventory?.available
          ? `${securityToolkitInventory.categoryCount} toolkit lanes | ${securityToolkitInventory.toolkitCount} visible entries.`
          : securityToolkitError || 'Inspect the authorized toolkit inventory and bounty export surface.',
        href: WATERFALL_SECURITY_ARCHITECT_ROUTE,
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Settings Snapshot',
        body: 'Inspect privacy posture, identity, and browser controls.',
        href: 'waterfall://settings',
        tone: 'lagoon'
      })}${buildNativeCard({
        title: 'Update Deck',
        body: updateManifest?.available
          ? `Signed update ${updateManifest.version} is ready for review.`
          : 'Inspect signed manifests, staged artifacts, and rollback posture.',
        href: WATERFALL_UPDATES_ROUTE,
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Search Deck',
        body: 'Open WaterFall native search with transparent provider lanes.',
        href: WATERFALL_SEARCH_ROUTE,
        tone: 'lagoon'
      })}${buildNativeCard({
        title: 'Collective Deck',
        body: settings.collective.enabled
          ? `Collective acceleration is armed at ${collectiveProjection.localUnits} planned units.`
          : 'Collective acceleration is currently offline.',
        href: 'waterfall://collective',
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Privacy Fortress',
        body: 'Inspect browser use cases, privacy posture, and protection targets.',
        href: 'waterfall://privacy-fortress',
        tone: 'lagoon'
      })}${buildNativeCard({
        title: 'Security Proof',
        body: 'Inspect security architecture, tests, and implementation evidence.',
        href: 'waterfall://security-proof',
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Engine Lab',
        body: 'Open the proving ground for the native renderer.',
        href: 'waterfall://engine-lab',
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Route Atlas',
        body: 'Survey every native route currently online.',
        href: 'waterfall://routes',
        tone: 'signal'
      })}` })}</section><section><h2>Quick Controls</h2>${buildNativeCluster({ columns: 2, children: `${buildNativeCard({
        title: 'Open Launch Pad Tab',
        body: 'Create a fresh blank WaterFall tab.',
        actionId: 'create-tab-launchpad',
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Open Home Page Tab',
        body: settings.homePage,
        actionId: 'create-tab-homepage',
        tone: 'lagoon'
      })}${buildNativeCard({
        title: 'Open Search Deck',
        body: 'Create a new native WaterFall search tab.',
        actionId: 'create-tab-search',
        tone: 'signal'
      })}${buildNativeCard({
        title: bookmarked ? 'Unpin Active Route' : 'Pin Active Route',
        body: activeTab.url || 'There is no active route to bookmark yet.',
        actionId: 'toggle-active-bookmark',
        tone: bookmarked ? 'ember' : 'signal'
      })}` })}</section><section><h2>Machine Profile</h2>${buildNativeCluster({ columns: 2, children: machineCards, tone: 'signal' })}</section></main>`
    };

    documents['waterfall://history'] = {
      route: 'waterfall://history',
      title: 'History Deck',
      subtitle: 'A native snapshot of recent routes seen by this WaterFall session.',
      markup: `<main data-wf-surface="hero" data-wf-tone="signal"><h1>History Deck</h1><p>Recent routes flowing through WaterFall. Every card below can reopen its route directly in this tab.</p><section><h2>Recent Routes</h2>${historyCards}</section><section><h2>History Controls</h2>${buildNativeCard({
        title: 'Clear History Deck',
        body: 'Wipe the current route memory and start fresh.',
        actionId: 'clear-history',
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Open Launch Pad Tab',
        body: 'Create a fresh blank WaterFall tab for the next route.',
        actionId: 'create-tab-launchpad',
        tone: 'signal'
      })}</section><section><h2>Native Hubs</h2>${buildNativeCard({
        title: 'Native Home',
        body: 'Return to the WaterFall dashboard.',
        href: 'waterfall://home',
        tone: 'lagoon'
      })}${buildNativeCard({
        title: 'Route Atlas',
        body: 'Open the native route index.',
        href: 'waterfall://routes',
        tone: 'signal'
      })}</section></main>`
    };

    documents['waterfall://bookmarks'] = {
      route: 'waterfall://bookmarks',
      title: 'Bookmark Deck',
      subtitle: 'Pinned routes rendered as a first-party WaterFall page.',
      markup: `<main data-wf-surface="hero" data-wf-tone="lagoon"><h1>Bookmark Deck</h1><p>These are the routes WaterFall is keeping close at hand. Every bookmark card navigates directly.</p><section><h2>Bookmarks</h2>${bookmarkCards}</section><section><h2>Native Hubs</h2>${buildNativeCard({
        title: 'History Deck',
        body: 'Open recent route memory.',
        href: 'waterfall://history',
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Native Home',
        body: 'Return to the WaterFall dashboard.',
        href: 'waterfall://home',
        tone: 'lagoon'
      })}</section></main>`
    };

    documents['waterfall://downloads'] = {
      route: 'waterfall://downloads',
      title: 'Download Hangar',
      subtitle: 'Live download state rendered through the native route lane.',
      markup: `<main data-wf-surface="hero" data-wf-tone="signal"><h1>Download Hangar</h1><p>WaterFall keeps local download state here. Download cards reveal their files directly from the blueprint.</p><section><h2>Recent Payloads</h2>${downloadCards}</section><section><h2>Native Hubs</h2>${buildNativeCard({
        title: 'Settings Snapshot',
        body: 'Inspect browser controls and storage posture.',
        href: 'waterfall://settings',
        tone: 'lagoon'
      })}${buildNativeCard({
        title: 'Security Workbench',
        body: 'Run scans, inspect quarantine posture, and export evidence bundles.',
        href: WATERFALL_SECURITY_WORKBENCH_ROUTE,
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Native Home',
        body: 'Return to the WaterFall dashboard.',
        href: 'waterfall://home',
        tone: 'lagoon'
      })}</section></main>`
    };

    documents[WATERFALL_SECURITY_WORKBENCH_ROUTE] = {
      route: WATERFALL_SECURITY_WORKBENCH_ROUTE,
      title: 'Security Workbench',
      subtitle: 'Operational download scanning, quarantine handling, and evidence export inside WaterFall.',
      markup: `<main data-wf-surface="hero" data-wf-tone="ember"><h1>Security Workbench</h1><p>WaterFall now runs preflight and postflight Download Gate scans inside the browser lifecycle. This deck exposes quarantine posture, orchestration health, and evidence export directly from the native surface.</p><section><h2>Security Posture</h2>${buildNativeCard({
        title: securityStatusLoading
          ? 'Refreshing Security Status'
          : securityStatus
            ? `Orchestrator ${securityStatus.orchestratorMode}`
            : 'Security Status Pending',
        body: securityStatus
          ? `VPN ${securityStatus.vpnEnabled ? 'enabled' : 'disabled'} | Download Gate ${securityStatus.downloadGateOnline ? 'online' : 'offline'} | Firewalls ${securityStatus.firewallProfiles.length} | Ledger ${securityStatus.ledgerHead || 'not yet advanced'}`
          : securityStatusError || 'WaterFall has not pulled a live security status snapshot yet.',
        tone: securityStatus
          ? securityStatus.orchestratorMode === 'online'
            ? 'lagoon'
            : 'signal'
          : 'signal'
      })}${buildNativeCard({
        title: 'Download Summary',
        body: `${securitySummary.totalDownloads} tracked | ${securitySummary.clean} clean | ${securitySummary.review} review | ${securitySummary.quarantined} quarantined | ${securitySummary.pending} pending`,
        tone: securitySummary.quarantined > 0 ? 'ember' : 'signal'
      })}${buildNativeCard({
        title: 'Export Security Report',
        body: 'Write the current security posture, download scans, and settings to a local evidence report.',
        actionId: 'export-security-report',
        tone: 'signal',
        surface: 'control'
      })}</section><section><h2>Download Gate Queue</h2>${securityWorkbenchCards}</section><section><h2>Native Hubs</h2>${buildNativeCard({
        title: 'Download Hangar',
        body: 'Return to the raw download deck.',
        href: 'waterfall://downloads',
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Site Shield',
        body: 'Inspect the active route and current browser guardrails.',
        href: WATERFALL_SITE_SHIELD_ROUTE,
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Security Proof',
        body: 'Inspect the broader security and validation surface.',
        href: 'waterfall://security-proof',
        tone: 'lagoon'
      })}${buildNativeCard({
        title: 'Settings Snapshot',
        body: 'Adjust download scanning and evidence export controls.',
        href: 'waterfall://settings',
        tone: 'signal'
      })}</section></main>`
    };

    documents[WATERFALL_SITE_SHIELD_ROUTE] = {
      route: WATERFALL_SITE_SHIELD_ROUTE,
      title: 'Site Shield',
      subtitle: 'A native site information and protection posture surface for the active route.',
      markup: `<main data-wf-surface="hero" data-wf-tone="signal"><h1>Site Shield</h1><p>WaterFall exposes the active route and the browser guardrails currently wrapped around it. This is the native site information and protection posture page for the active tab.</p><section><h2>Active Route</h2>${buildNativeCard({
        title: activeTab.title || 'Active Route',
        body: `${activeRouteSummary.displayUrl} | host ${activeRouteSummary.host} | protocol ${activeRouteSummary.protocol} | lane ${activeRouteSummary.lane}`,
        tone:
          activeRouteSummary.protocol === 'https:' || activeRouteSummary.protocol === 'waterfall:'
            ? 'lagoon'
            : 'ember'
      })}${buildNativeCard({
        title: 'Protection Posture',
        body: `DNT ${settings.privacy.doNotTrack ? 'on' : 'off'} | GPC ${settings.privacy.globalPrivacyControl ? 'on' : 'off'} | HTTPS upgrades ${settings.privacy.httpsOnlyMode ? 'on' : 'off'} | trackers ${settings.privacy.blockTrackers ? 'blocked' : 'pass-through'} | kill switch ${settings.privacy.masterKillSwitch ? 'armed' : 'idle'} | permissions ${settings.privacy.permissionsLockdown ? 'locked' : 'open'} | popups ${settings.privacy.blockPopups ? 'blocked' : 'external'} | referrers ${settings.privacy.stripReferrers ? 'stripped' : 'pass-through'} | fingerprint shaping ${settings.privacy.antiFingerprinting ? 'on' : 'off'}`,
        tone: 'signal'
      })}${buildNativeCard({
        title: securityStatus
          ? `Orchestrator ${securityStatus.orchestratorMode}`
          : 'Security Status Pending',
        body: securityStatus
          ? `VPN ${securityStatus.vpnEnabled ? 'enabled' : 'disabled'} | Download Gate ${securityStatus.downloadGateOnline ? 'online' : 'offline'} | Firewalls ${securityStatus.firewallProfiles.join(' | ') || 'none surfaced'}`
          : securityStatusError || 'WaterFall has not pulled the live orchestrator posture yet.',
        tone: securityStatus?.orchestratorMode === 'online' ? 'lagoon' : 'signal'
      })}</section><section><h2>Native Hubs</h2>${buildNativeCard({
        title: 'Security Workbench',
        body: 'Operate download scanning, quarantine, and evidence export.',
        href: WATERFALL_SECURITY_WORKBENCH_ROUTE,
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Settings Snapshot',
        body: 'Adjust browser guardrails and download security controls.',
        href: 'waterfall://settings',
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Privacy Auditor',
        body: 'Review bridge health, privacy posture, and exposure surfaces.',
        href: WATERFALL_PRIVACY_AUDITOR_ROUTE,
        tone: 'lagoon'
      })}${buildNativeCard({
        title: 'Native Home',
        body: 'Return to the WaterFall dashboard.',
        href: WATERFALL_HOME_ROUTE,
        tone: 'lagoon'
      })}</section></main>`
    };

    documents[WATERFALL_PRIVACY_AUDITOR_ROUTE] = {
      route: WATERFALL_PRIVACY_AUDITOR_ROUTE,
      title: 'Privacy Auditor',
      subtitle: 'Native visibility into bridge health, privacy posture, and current exposure surfaces.',
      markup: `<main data-wf-surface="hero" data-wf-tone="lagoon"><h1>Privacy Auditor</h1><p>WaterFall surfaces the privacy posture of this browser shell directly in the native lane. This deck ties together bridge health, route guardrails, download exposure, and live browser settings.</p><section><h2>Control Plane</h2>${buildNativeCard({
        title: bridgeHealthLoading
          ? 'Refreshing Bridge Health'
          : bridgeHealth
            ? `Bridge ${bridgeHealth.mode}`
            : 'Bridge Health Pending',
        body: bridgeHealth
          ? `${bridgeHealth.transport} | ${bridgeHealth.endpoint} | ${bridgeHealth.capabilities.length} capability lane(s)`
          : bridgeHealthError || 'WaterFall has not pulled the bridge health surface yet.',
        tone: bridgeHealth?.connected ? 'lagoon' : 'signal'
      })}${buildNativeCard({
        title: 'Privacy Posture',
        body: `${privacyPosture.score}% | ${privacyPosture.enabled}/${privacyPosture.total} guardrails armed | DNT ${settings.privacy.doNotTrack ? 'on' : 'off'} | GPC ${settings.privacy.globalPrivacyControl ? 'on' : 'off'}`,
        tone: privacyPosture.score >= 75 ? 'lagoon' : 'ember'
      })}${buildNativeCard({
        title: 'Exposure Surface',
        body: `${tabs.length} tab(s) | ${history.length} history entries | ${bookmarks.length} bookmarks | ${securitySummary.totalDownloads} tracked downloads`,
        tone: securitySummary.quarantined > 0 ? 'ember' : 'signal'
      })}</section><section><h2>Auditor Controls</h2>${buildNativeCard({
        title: securityStatus?.vpnEnabled ? 'Disable Sovereign VPN' : 'Enable Sovereign VPN',
        body: securityStatus?.vpnEnabled
          ? 'Ask the orchestrator bridge to stand the built-in VPN down.'
          : 'Ask the orchestrator bridge to raise the built-in VPN lane.',
        actionId: securityStatus?.vpnEnabled ? 'disable-vpn' : 'enable-vpn',
        tone: securityStatus?.vpnEnabled ? 'ember' : 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: 'Export Security Report',
        body: 'Write the current posture to a local evidence report.',
        actionId: 'export-security-report',
        tone: 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: 'Check Update Integrity',
        body: 'Refresh the signed update deck and current rollback posture.',
        actionId: 'check-updates',
        tone: 'ember',
        surface: 'control'
      })}</section><section><h2>Native Hubs</h2>${buildNativeCard({
        title: 'Site Shield',
        body: 'Inspect the active route and its protection posture.',
        href: WATERFALL_SITE_SHIELD_ROUTE,
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Security Workbench',
        body: 'Operate Download Gate, quarantine, and report export.',
        href: WATERFALL_SECURITY_WORKBENCH_ROUTE,
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Security Architect',
        body: 'Inspect the toolkit inventory and export bounty-ready evidence packs.',
        href: WATERFALL_SECURITY_ARCHITECT_ROUTE,
        tone: 'ember'
      })}</section></main>`
    };

    documents[WATERFALL_SECURITY_ARCHITECT_ROUTE] = {
      route: WATERFALL_SECURITY_ARCHITECT_ROUTE,
      title: 'Security Architect',
      subtitle: 'Authorized toolkit visibility and bounty-ready evidence export inside WaterFall.',
      markup: `<main data-wf-surface="hero" data-wf-tone="ember"><h1>Security Architect</h1><p>This deck exposes WaterFall’s authorized security-architect lane: scoped artifact scanning, strict-scope posture, and the local penetration-testing toolkit inventory already present in the sovereign workspace.</p><section><h2>Scope And Consent</h2>${buildNativeCard({
        title: 'Authorization Posture',
        body: `Strict scope ${settings.security.strictScopeMode ? 'enabled' : 'disabled'} | native scanning ${settings.security.nativeArtifactScanning ? 'enabled' : 'disabled'} | external authorized scanning ${settings.security.externalAuthorizedScanning ? 'enabled' : 'disabled'}`,
        tone: settings.security.strictScopeMode ? 'lagoon' : 'ember'
      })}${buildNativeCard({
        title: 'Toolkit Root',
        body: securityToolkitInventory?.available
          ? `${securityToolkitInventory.rootPath} | ${securityToolkitInventory.categoryCount} category lanes`
          : securityToolkitError || 'WaterFall has not surfaced the toolkit root yet.',
        tone: securityToolkitInventory?.available ? 'signal' : 'ember'
      })}${buildNativeCard({
        title: 'Bounty Pack Export',
        body: 'Write a markdown + JSON evidence bundle for review or existing bounty submission flows.',
        actionId: 'export-bounty-pack',
        tone: 'ember',
        surface: 'control'
      })}</section><section><h2>Toolkit Inventory</h2>${toolkitCategoryCards}</section><section><h2>Native Hubs</h2>${buildNativeCard({
        title: 'Security Workbench',
        body: 'Operate Download Gate and quarantine from the browser shell.',
        href: WATERFALL_SECURITY_WORKBENCH_ROUTE,
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Privacy Auditor',
        body: 'Review bridge health and browser exposure surfaces.',
        href: WATERFALL_PRIVACY_AUDITOR_ROUTE,
        tone: 'lagoon'
      })}${buildNativeCard({
        title: 'Route Atlas',
        body: 'Survey the rest of the native browser surfaces.',
        href: 'waterfall://routes',
        tone: 'signal'
      })}</section></main>`
    };

    documents[WATERFALL_UPDATES_ROUTE] = {
      route: WATERFALL_UPDATES_ROUTE,
      title: 'Update Deck',
      subtitle: 'Signed manifest verification, staged artifacts, and rollback posture for WaterFall.',
      markup: `<main data-wf-surface="hero" data-wf-tone="ember"><h1>Update Deck</h1><p>WaterFall verifies signed release manifests in the main process, stages verified artifacts locally, and records rollback posture before handing control back to the orchestrator.</p><section><h2>Verification Status</h2>${updateSummaryCards}${buildNativeCard({
        title: updatesLoading ? 'Updater Busy' : 'Check For Updates',
        body: updatesLoading
          ? 'WaterFall is actively checking the signed release lane.'
          : 'Ask WaterFall to pull the latest signed manifest and refresh the verification state.',
        actionId: 'check-updates',
        tone: updatesLoading ? 'signal' : 'lagoon',
        surface: 'control'
      })}${buildNativeCard({
        title:
          updateManifestReady
            ? `Stage Update ${updateManifest?.version || ''}`
            : 'Stage Verified Update',
        body:
          updateManifestReady
            ? 'Stage the verified artifact locally and capture rollback metadata.'
            : 'WaterFall will only stage an update after the manifest verifies.',
        actionId: 'apply-update',
        tone:
          updateManifestReady ? 'ember' : 'signal',
        surface: 'control'
      })}</section><section><h2>Release Notes</h2>${updateNoteCards}</section><section><h2>Native Hubs</h2>${buildNativeCard({
        title: 'Settings Snapshot',
        body: 'Open the browser settings and backup surface.',
        href: 'waterfall://settings',
        tone: 'lagoon'
      })}${buildNativeCard({
        title: 'Security Proof',
        body: 'Inspect the validation and enforcement deck.',
        href: 'waterfall://security-proof',
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Native Home',
        body: 'Return to the WaterFall dashboard.',
        href: WATERFALL_HOME_ROUTE,
        tone: 'lagoon'
      })}</section></main>`
    };

    documents['waterfall://settings'] = {
      route: 'waterfall://settings',
      title: 'Settings Snapshot',
      subtitle: 'A native readout of browser identity, privacy posture, and collective controls.',
      markup: `<main data-wf-surface="hero" data-wf-tone="lagoon"><h1>Settings Snapshot</h1><p>WaterFall is exposing its current browser state as a native page. These cards can open the live drawer, flip core browser settings, or move you deeper into related native decks.</p><section><h2>Browser Identity</h2>${buildNativeCard({
        title: 'Browser Profile',
        body: `Home page: ${settings.homePage} | Search: ${SEARCH_ENGINE_LABELS[settings.searchEngine]} | Restore session: ${settings.restoreSession ? 'enabled' : 'disabled'}`,
        tone: 'lagoon'
      })}${buildNativeCard({
        title: 'Open Settings Drawer',
        body: 'Jump into the full editable settings deck inside WaterFall.',
        actionId: 'open-settings',
        tone: 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: 'Copy Node Identity',
        body: `${settings.account.displayName} | ${settings.account.nodeId}`,
        actionId: 'copy-node',
        tone: 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: `Restore Session ${settings.restoreSession ? 'On' : 'Off'}`,
        body: 'Toggle whether WaterFall reopens the last browser session on launch.',
        actionId: 'toggle-restore-session',
        tone: settings.restoreSession ? 'lagoon' : 'ember',
        surface: 'control'
      })}</section><section><h2>Native Inputs</h2>${buildNativeControl({
        kind: 'text',
        settingPath: 'homePage',
        label: 'Custom Home Route',
        caption: 'Set the browser home page to a waterfall://, http://, or https:// target.',
        stringValue: settings.homePage,
        placeholder: 'waterfall://home',
        tone: 'lagoon'
      })}${buildNativeControl({
        kind: 'select',
        settingPath: 'searchEngine',
        label: 'Search Engine',
        caption: 'Choose the lead provider lane for WaterFall native search queries.',
        stringValue: settings.searchEngine,
        options: SEARCH_ENGINE_CONTROL_OPTIONS,
        tone: 'signal'
      })}</section><section><h2>Home And Search Presets</h2>${buildNativeCard({
        title: 'Set Home To Native Search',
        body: 'Use waterfall://search as the browser home page.',
        actionId: 'set-home-search',
        tone: settings.homePage === WATERFALL_SEARCH_ROUTE ? 'lagoon' : 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: 'Set Home To Native Home',
        body: 'Use waterfall://home as the browser home page.',
        actionId: 'set-home-native',
        tone: settings.homePage === 'waterfall://home' ? 'lagoon' : 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: 'Set Home To DuckDuckGo',
        body: 'Use https://duckduckgo.com as the browser home page.',
        actionId: 'set-home-duckduckgo',
        tone: settings.homePage === 'https://duckduckgo.com' ? 'lagoon' : 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: 'Set Home To Startpage',
        body: 'Use https://www.startpage.com as the browser home page.',
        actionId: 'set-home-startpage',
        tone: settings.homePage === 'https://www.startpage.com' ? 'lagoon' : 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: 'Search Engine DuckDuckGo',
        body: 'Make DuckDuckGo the lead provider lane for WaterFall native search.',
        actionId: 'set-search-duckduckgo',
        tone: settings.searchEngine === 'duckduckgo' ? 'lagoon' : 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: 'Search Engine Startpage',
        body: 'Make Startpage the lead provider lane for WaterFall native search.',
        actionId: 'set-search-startpage',
        tone: settings.searchEngine === 'startpage' ? 'lagoon' : 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: 'Search Engine Kagi',
        body: 'Make Kagi the lead provider lane for WaterFall native search.',
        actionId: 'set-search-kagi',
        tone: settings.searchEngine === 'kagi' ? 'lagoon' : 'signal',
        surface: 'control'
      })}</section><section><h2>Privacy And Compute</h2>${buildNativeCard({
        title: 'Privacy Posture',
        body: `DNT ${settings.privacy.doNotTrack ? 'on' : 'off'} | GPC ${settings.privacy.globalPrivacyControl ? 'on' : 'off'} | HTTPS upgrades ${settings.privacy.httpsOnlyMode ? 'on' : 'off'} | tracker blocking ${settings.privacy.blockTrackers ? 'on' : 'off'} | kill switch ${settings.privacy.masterKillSwitch ? 'armed' : 'idle'} | popup blocker ${settings.privacy.blockPopups ? 'on' : 'off'}`,
        tone: 'signal'
      })}${buildNativeCard({
        title: `Do Not Track ${settings.privacy.doNotTrack ? 'On' : 'Off'}`,
        body: 'Toggle the DNT request header for WaterFall web traffic.',
        actionId: 'toggle-dnt',
        tone: settings.privacy.doNotTrack ? 'signal' : 'ember',
        surface: 'control'
      })}${buildNativeCard({
        title: `Global Privacy Control ${settings.privacy.globalPrivacyControl ? 'On' : 'Off'}`,
        body: 'Toggle GPC headers for supported sites.',
        actionId: 'toggle-gpc',
        tone: settings.privacy.globalPrivacyControl ? 'signal' : 'ember',
        surface: 'control'
      })}${buildNativeCard({
        title: `HTTPS Upgrades ${settings.privacy.httpsOnlyMode ? 'On' : 'Off'}`,
        body: 'Toggle WaterFall public-route upgrades from http to https.',
        actionId: 'toggle-https-only',
        tone: settings.privacy.httpsOnlyMode ? 'signal' : 'ember',
        surface: 'control'
      })}${buildNativeCard({
        title: `Tracker Blocking ${settings.privacy.blockTrackers ? 'On' : 'Off'}`,
        body: 'Toggle blocking for the known tracker host list.',
        actionId: 'toggle-block-trackers',
        tone: settings.privacy.blockTrackers ? 'signal' : 'ember',
        surface: 'control'
      })}${buildNativeCard({
        title: `Master Kill Switch ${settings.privacy.masterKillSwitch ? 'Armed' : 'Idle'}`,
        body: 'Cancel every outgoing http and https request from the WaterFall browser partition instantly.',
        actionId: 'toggle-kill-switch',
        tone: settings.privacy.masterKillSwitch ? 'ember' : 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: `Permissions Lockdown ${settings.privacy.permissionsLockdown ? 'On' : 'Off'}`,
        body: 'Deny guest permission checks and requests unless you explicitly turn the lockdown off.',
        actionId: 'toggle-permissions-lockdown',
        tone: settings.privacy.permissionsLockdown ? 'signal' : 'ember',
        surface: 'control'
      })}${buildNativeCard({
        title: `Strip Referrers ${settings.privacy.stripReferrers ? 'On' : 'Off'}`,
        body: 'Remove referrer headers from guest browser traffic.',
        actionId: 'toggle-strip-referrers',
        tone: settings.privacy.stripReferrers ? 'signal' : 'ember',
        surface: 'control'
      })}${buildNativeCard({
        title: `Anti-Fingerprinting ${settings.privacy.antiFingerprinting ? 'On' : 'Off'}`,
        body: 'Shape the user agent and remove client-hint headers before requests leave WaterFall.',
        actionId: 'toggle-anti-fingerprinting',
        tone: settings.privacy.antiFingerprinting ? 'signal' : 'ember',
        surface: 'control'
      })}${buildNativeCard({
        title: `Popup Blocker ${settings.privacy.blockPopups ? 'On' : 'Off'}`,
        body: 'Control whether guest popup attempts are blocked or handed off externally.',
        actionId: 'toggle-block-popups',
        tone: settings.privacy.blockPopups ? 'signal' : 'ember',
        surface: 'control'
      })}${buildNativeCard({
        title: 'Collective Deck',
        body: `Opt-in ${settings.collective.enabled ? 'enabled' : 'disabled'} | CPU ${settings.collective.cpuLimitPercent}% | GPU ${settings.collective.gpuLimitPercent}%`,
        href: 'waterfall://collective',
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Extension Deck',
        body: `${extensions.length} extension record(s) are tracked right now.`,
        href: 'waterfall://extensions',
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Security Workbench',
        body: `Preflight ${settings.security.scanDownloadsOnStart ? 'on' : 'off'} | Postflight ${settings.security.scanDownloadsOnCompletion ? 'on' : 'off'} | Evidence ${settings.security.exportEvidenceBundles ? 'on' : 'off'}`,
        href: WATERFALL_SECURITY_WORKBENCH_ROUTE,
        tone: 'ember'
      })}</section><section><h2>Security Controls</h2>${buildNativeCard({
        title: `Preflight Scans ${settings.security.scanDownloadsOnStart ? 'On' : 'Off'}`,
        body: 'Toggle Download Gate checks before downloads are written to disk.',
        actionId: 'toggle-scan-downloads-on-start',
        tone: settings.security.scanDownloadsOnStart ? 'signal' : 'ember',
        surface: 'control'
      })}${buildNativeCard({
        title: `Postflight Scans ${settings.security.scanDownloadsOnCompletion ? 'On' : 'Off'}`,
        body: 'Toggle Download Gate checks after downloads complete.',
        actionId: 'toggle-scan-downloads-on-completion',
        tone: settings.security.scanDownloadsOnCompletion ? 'signal' : 'ember',
        surface: 'control'
      })}${buildNativeCard({
        title: `Quarantine High-Risk ${settings.security.quarantineHighRiskDownloads ? 'On' : 'Off'}`,
        body: 'Toggle automatic quarantine for risky artifacts.',
        actionId: 'toggle-quarantine-high-risk-downloads',
        tone: settings.security.quarantineHighRiskDownloads ? 'ember' : 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: `Native Artifact Scanning ${settings.security.nativeArtifactScanning ? 'On' : 'Off'}`,
        body: 'Keep local artifact inspection active inside WaterFall.',
        actionId: 'toggle-native-artifact-scanning',
        tone: settings.security.nativeArtifactScanning ? 'signal' : 'ember',
        surface: 'control'
      })}${buildNativeCard({
        title: `Authorized External Scanning ${settings.security.externalAuthorizedScanning ? 'On' : 'Off'}`,
        body: 'Allow explicitly authorized external target flows in the workbench.',
        actionId: 'toggle-external-authorized-scanning',
        tone: settings.security.externalAuthorizedScanning ? 'ember' : 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: `Evidence Export ${settings.security.exportEvidenceBundles ? 'On' : 'Off'}`,
        body: 'Toggle whether the workbench exposes exportable evidence bundles.',
        actionId: 'toggle-export-evidence-bundles',
        tone: settings.security.exportEvidenceBundles ? 'signal' : 'ember',
        surface: 'control'
      })}</section><section><h2>Architecture Routes</h2>${buildNativeCard({
        title: 'Orchestrator Deck',
        body: 'Map the privacy-first system architecture and browser control plane.',
        href: 'waterfall://orchestrator',
        tone: 'lagoon'
      })}${buildNativeCard({
        title: 'Privacy Fortress',
        body: 'Review use cases and the protective stance for this browser.',
        href: 'waterfall://privacy-fortress',
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Security Proof',
        body: 'Inspect security features, examples, tests, and implementation evidence.',
        href: 'waterfall://security-proof',
        tone: 'signal'
      })}</section><section><h2>Machine Profile</h2>${machineCards}</section></main>`
    };

    documents['waterfall://session'] = {
      route: 'waterfall://session',
      title: 'Session Deck',
      subtitle: 'Open tabs and active session memory from the current browser shell.',
      markup: `<main data-wf-surface="hero" data-wf-tone="signal"><h1>Session Deck</h1><p>WaterFall is surfacing its open tabs as a native page. Tab cards below navigate directly, even for ordinary web routes.</p><section><h2>Open Tabs</h2>${sessionCards}</section><section><h2>Session Controls</h2>${buildNativeCard({
        title: 'Open Launch Pad Tab',
        body: 'Create a fresh blank WaterFall tab.',
        actionId: 'create-tab-launchpad',
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Open Native Home Tab',
        body: 'Create a new waterfall://home tab.',
        actionId: 'create-tab-home',
        tone: 'lagoon'
      })}${buildNativeCard({
        title: 'Duplicate Active Route',
        body: activeTab.url || settings.homePage,
        actionId: 'duplicate-active-tab',
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Clear History Deck',
        body: 'Drop the current route memory while keeping tabs alive.',
        actionId: 'clear-history',
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Reset Session',
        body: `Restore session is ${settings.restoreSession ? 'enabled' : 'disabled'} and the active tab id is ${activeTabId}. Use this to reopen a fresh launch pad.`,
        actionId: 'reset-session',
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Route Atlas',
        body: 'Open the native route index.',
        href: 'waterfall://routes',
        tone: 'signal'
      })}</section></main>`
    };

    documents['waterfall://extensions'] = {
      route: 'waterfall://extensions',
      title: 'Extension Deck',
      subtitle: 'Trusted extension state rendered as a first-party page.',
      markup: `<main data-wf-surface="hero" data-wf-tone="ember"><h1>Extension Deck</h1><p>WaterFall keeps extension state in its isolated partition. Extension cards remove the selected package from this browser profile.</p><section><h2>Loaded Extensions</h2>${extensionCards}</section><section><h2>Extension Controls</h2>${buildNativeCard({
        title: 'Add Trusted Extension',
        body: 'Open the native extension picker and load an unpacked extension.',
        actionId: 'add-extension',
        tone: 'signal',
        surface: 'control'
      })}</section><section><h2>Native Hubs</h2>${buildNativeCard({
        title: 'Open Settings Drawer',
        body: 'Manage unpacked extensions from the live settings deck.',
        actionId: 'open-extension-settings',
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Settings Snapshot',
        body: 'Open the native settings readout.',
        href: 'waterfall://settings',
        tone: 'lagoon'
      })}</section></main>`
    };

    documents['waterfall://collective'] = {
      route: 'waterfall://collective',
      title: 'Collective Deck',
      subtitle: 'Native visibility into shared-compute posture, limits, and machine capacity.',
      markup: `<main data-wf-surface="hero" data-wf-tone="ember"><h1>Collective Deck</h1><p>The collective plane remains explicit and opt-in. This page shows the current pledge math and lets you jump straight to the matching controls.</p><section><h2>Contribution Posture</h2>${buildNativeCard({
        title: 'Current Posture',
        body: `Enabled ${settings.collective.enabled ? 'yes' : 'no'} | CPU sharing ${settings.collective.cpuEnabled ? 'yes' : 'no'} | GPU sharing ${settings.collective.gpuEnabled ? 'yes' : 'no'} | Session cap ${settings.collective.sessionCapMinutes} minutes`,
        tone: 'ember'
      })}${buildNativeCard({
        title: `Collective Mesh ${settings.collective.enabled ? 'On' : 'Off'}`,
        body: 'Toggle whether this browser can join the future shared-compute mesh.',
        actionId: 'toggle-collective-enabled',
        tone: settings.collective.enabled ? 'signal' : 'ember',
        surface: 'control'
      })}${buildNativeCard({
        title: `CPU Sharing ${settings.collective.cpuEnabled ? 'On' : 'Off'}`,
        body: 'Toggle whether CPU capacity may be pledged to the collective.',
        actionId: 'toggle-collective-cpu',
        tone: settings.collective.cpuEnabled ? 'signal' : 'ember',
        surface: 'control'
      })}${buildNativeCard({
        title: `GPU Sharing ${settings.collective.gpuEnabled ? 'On' : 'Off'}`,
        body: resourceProfile?.gpu.devices.length
          ? 'Toggle whether detected GPU capacity may be pledged to the collective.'
          : 'No GPU device is currently available to share.',
        actionId: 'toggle-collective-gpu',
        tone: settings.collective.gpuEnabled ? 'signal' : 'ember',
        surface: 'control'
      })}${buildNativeCard({
        title: 'Projection',
        body: `Local pledge ${collectiveProjection.localUnits} units | 8 peers ${collectiveProjection.projections[0]?.units || 0} | 64 peers ${collectiveProjection.projections[1]?.units || 0} | 512 peers ${collectiveProjection.projections[2]?.units || 0}`,
        tone: 'signal'
      })}</section><section><h2>Native Sliders</h2>${buildNativeControl({
        kind: 'range',
        settingPath: 'collective.cpuLimitPercent',
        label: 'CPU Pledge Cap',
        caption: 'Move the CPU contribution limit without leaving the native page.',
        numberValue: settings.collective.cpuLimitPercent,
        min: 5,
        max: 90,
        step: 5,
        tone: 'signal'
      })}${buildNativeControl({
        kind: 'range',
        settingPath: 'collective.gpuLimitPercent',
        label: 'GPU Pledge Cap',
        caption: 'Move the GPU contribution limit without leaving the native page.',
        numberValue: settings.collective.gpuLimitPercent,
        min: 5,
        max: 90,
        step: 5,
        tone: 'ember'
      })}${buildNativeControl({
        kind: 'range',
        settingPath: 'collective.sessionCapMinutes',
        label: 'Session Cap Minutes',
        caption: 'Control how long this browser may contribute to the collective per session.',
        numberValue: settings.collective.sessionCapMinutes,
        min: 5,
        max: 240,
        step: 5,
        tone: 'lagoon'
      })}${buildNativeCard({
        title: `CPU Cap ${settings.collective.cpuLimitPercent}%`,
        body: 'Reduce the CPU pledge cap by 5 percent.',
        actionId: 'cpu-cap-down',
        tone: 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: `CPU Cap ${settings.collective.cpuLimitPercent}%`,
        body: 'Increase the CPU pledge cap by 5 percent.',
        actionId: 'cpu-cap-up',
        tone: 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: `GPU Cap ${settings.collective.gpuLimitPercent}%`,
        body: 'Reduce the GPU pledge cap by 5 percent.',
        actionId: 'gpu-cap-down',
        tone: 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: `GPU Cap ${settings.collective.gpuLimitPercent}%`,
        body: 'Increase the GPU pledge cap by 5 percent.',
        actionId: 'gpu-cap-up',
        tone: 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: `Session Cap ${settings.collective.sessionCapMinutes} min`,
        body: 'Lower the collective session cap by 5 minutes.',
        actionId: 'session-cap-down',
        tone: 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: `Session Cap ${settings.collective.sessionCapMinutes} min`,
        body: 'Raise the collective session cap by 5 minutes.',
        actionId: 'session-cap-up',
        tone: 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: 'Open Collective Controls',
        body: 'Jump into the live settings drawer for CPU, GPU, and consent controls.',
        actionId: 'collective-settings',
        tone: 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: 'Refresh Projection',
        body: 'Ask the native renderer for a fresh collective render pass.',
        actionId: 'refresh-collective',
        tone: 'signal',
        surface: 'control'
      })}${buildNativeCard({
        title: 'Mesh Deck',
        body: 'Inspect trust posture and node identity.',
        href: 'waterfall://mesh',
        tone: 'lagoon'
      })}${buildNativeCard({
        title: 'Privacy Fortress',
        body: 'Review how the browser positions privacy, leak protection, and kill-switch goals.',
        href: 'waterfall://privacy-fortress',
        tone: 'signal'
      })}</section><section><h2>Machine Profile</h2>${machineCards}</section></main>`
    };

    documents['waterfall://mesh'] = {
      route: 'waterfall://mesh',
      title: 'Mesh Deck',
      subtitle: 'Identity and trust posture for WaterFall peer orchestration.',
      markup: `<main data-wf-surface="hero" data-wf-tone="lagoon"><h1>Mesh Deck</h1><p>WaterFall's mesh identity is present even before the full peer protocol ships. This page now exposes direct blueprint actions for copy and control flow.</p><section><h2>Identity And Trust</h2>${buildNativeCard({
        title: 'Node Identity',
        body: `${settings.account.displayName} | node ${settings.account.nodeId} | device ${settings.account.deviceName}`,
        actionId: 'mesh-copy-node',
        tone: 'lagoon'
      })}${buildNativeCard({
        title: 'Trust Posture',
        body: `Protocol ${settings.mesh.protocolVersion} | trust mode ${settings.mesh.trustMode} | peers ${settings.mesh.peers.length}`,
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Open Mesh Controls',
        body: 'Jump into the live settings drawer for identity and future mesh consent.',
        actionId: 'mesh-settings',
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Collective Deck',
        body: 'Return to the compute contribution page.',
        href: 'waterfall://collective',
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Route Atlas',
        body: 'Survey the rest of the native route network.',
        href: 'waterfall://routes',
        tone: 'signal'
      })}</section></main>`
    };

    documents['waterfall://routes'] = {
      route: 'waterfall://routes',
      title: 'Route Atlas',
      subtitle: 'The native page index for WaterFall.',
      markup: `<main data-wf-surface="hero" data-wf-tone="signal"><h1>Route Atlas</h1><p>These are the first-party routes WaterFall can serve right now. Every route card below is live.</p><section><h2>Available Native Routes</h2>${routeCards}</section></main>`
    };

    documents['waterfall://orchestrator'] = {
      route: 'waterfall://orchestrator',
      title: 'Orchestrator Deck',
      subtitle: 'The privacy-first architecture map behind Thirsty\'s WaterFall.',
      markup: `<main data-wf-surface="hero" data-wf-tone="lagoon"><h1>Orchestrator Deck</h1><p>Everything in the original design plan routes through one encrypted control plane: browser shell, firewall stack, VPN lane, privacy engines, and hard security systems. This page captures that architecture inside WaterFall itself.</p><section><h2>System Overview</h2>${orchestratorSystemCards}</section><section><h2>Route Links</h2>${buildNativeCard({
        title: 'Privacy Fortress',
        body: 'Open the browser use cases and protection targets.',
        href: 'waterfall://privacy-fortress',
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Security Proof',
        body: 'Inspect security architecture, tests, examples, and implementation evidence.',
        href: 'waterfall://security-proof',
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Settings Snapshot',
        body: 'Open the live browser settings surface.',
        href: 'waterfall://settings',
        tone: 'lagoon'
      })}${buildNativeCard({
        title: 'Collective Deck',
        body: 'Open the shared-compute consent and cap controls.',
        href: 'waterfall://collective',
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Route Atlas',
        body: 'Survey the rest of the native browser routes.',
        href: 'waterfall://routes',
        tone: 'signal'
      })}</section></main>`
    };

    documents['waterfall://privacy-fortress'] = {
      route: 'waterfall://privacy-fortress',
      title: 'Privacy Fortress',
      subtitle: 'Use cases, privacy intent, and the current protective posture for WaterFall.',
      markup: `<main data-wf-surface="hero" data-wf-tone="ember"><h1>Privacy Fortress</h1><p>WaterFall is aiming at maximum privacy browsing, secure research, anonymous communication, leak-proof networking, and clean browsing with no popup chaos. This page ties those use cases back to the live browser state.</p><section><h2>Use Cases</h2>${privacyUseCaseCards}</section><section><h2>Operational Routes</h2>${buildNativeCard({
        title: 'Settings Snapshot',
        body: 'Open the live privacy toggles and browser settings.',
        href: 'waterfall://settings',
        tone: 'lagoon'
      })}${buildNativeCard({
        title: 'Orchestrator Deck',
        body: 'Inspect the full architecture map behind the privacy plan.',
        href: 'waterfall://orchestrator',
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Security Proof',
        body: 'Inspect the threat model, validation posture, and implementation proof surface.',
        href: 'waterfall://security-proof',
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Security Workbench',
        body: 'Operate Download Gate, quarantine, and evidence export from the native browser surface.',
        href: WATERFALL_SECURITY_WORKBENCH_ROUTE,
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Download Hangar',
        body: 'Review local payload tracking inside the browser shell.',
        href: 'waterfall://downloads',
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Security Workbench',
        body: 'Operate Download Gate, quarantine, and evidence export in-browser.',
        href: WATERFALL_SECURITY_WORKBENCH_ROUTE,
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Extension Deck',
        body: 'Review extension isolation and package controls.',
        href: 'waterfall://extensions',
        tone: 'ember'
      })}</section></main>`
    };

    documents['waterfall://security-proof'] = {
      route: 'waterfall://security-proof',
      title: 'Security Proof',
      subtitle: 'Security posture, tests, examples, and implementation evidence for WaterFall.',
      markup: `<main data-wf-surface="hero" data-wf-tone="signal"><h1>Security Proof</h1><p>WaterFall’s security story needs proof, not slogans. This page captures the threat-model expectations, documentation posture, examples, test coverage, and implementation evidence you outlined.</p><section><h2>Security And Validation</h2>${securityProofCards}</section><section><h2>Operational Routes</h2>${buildNativeCard({
        title: 'Settings Snapshot',
        body: 'Open the live browser settings surface.',
        href: 'waterfall://settings',
        tone: 'lagoon'
      })}${buildNativeCard({
        title: 'Orchestrator Deck',
        body: 'Inspect the system architecture map.',
        href: 'waterfall://orchestrator',
        tone: 'signal'
      })}${buildNativeCard({
        title: 'Privacy Fortress',
        body: 'Return to browser use cases and privacy posture.',
        href: 'waterfall://privacy-fortress',
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Security Workbench',
        body: 'Operate download scanning, quarantine, and evidence export.',
        href: WATERFALL_SECURITY_WORKBENCH_ROUTE,
        tone: 'ember'
      })}${buildNativeCard({
        title: 'Route Atlas',
        body: 'Survey the rest of the native WaterFall routes.',
        href: 'waterfall://routes',
        tone: 'signal'
      })}</section></main>`
    };

    return documents;
  }, [
    activeTabId,
    bookmarks,
    bridgeHealth,
    bridgeHealthError,
    bridgeHealthLoading,
    collectiveProjection,
    downloads,
    extensions,
    history,
    privacyPosture,
    resourceProfile,
    securityStatus,
    securityStatusError,
    securityStatusLoading,
    securitySummary,
    securityToolkitError,
    securityToolkitInventory,
    securityToolkitLoading,
    searchRouteStates,
    settings,
    siteShieldTargetUrl,
    updateError,
    updateManifest,
    updatesLoading,
    tabs
  ]);
  const nativeRouteActionsByRoute = useMemo(() => {
    const actions: Record<string, WaterfallNativeRouteAction[]> = {};
    const staticRouteActions = [
      {
        id: 'go-home',
        title: 'Native Home',
        caption: 'Open WaterFall native home.',
        kind: 'navigate' as const,
        target: WATERFALL_HOME_ROUTE
      },
      {
        id: 'go-search',
        title: 'Search Deck',
        caption: 'Open the native WaterFall search surface.',
        kind: 'navigate' as const,
        target: WATERFALL_SEARCH_ROUTE
      },
      {
        id: 'go-history',
        title: 'History Deck',
        caption: 'Open the live route history page.',
        kind: 'navigate' as const,
        target: 'waterfall://history'
      },
      {
        id: 'go-bookmarks',
        title: 'Bookmark Deck',
        caption: 'Open pinned routes.',
        kind: 'navigate' as const,
        target: 'waterfall://bookmarks'
      },
      {
        id: 'go-downloads',
        title: 'Download Hangar',
        caption: 'Open the native download deck.',
        kind: 'navigate' as const,
        target: 'waterfall://downloads'
      },
      {
        id: 'go-security-workbench',
        title: 'Security Workbench',
        caption: 'Inspect scans, quarantine posture, and evidence export.',
        kind: 'navigate' as const,
        target: WATERFALL_SECURITY_WORKBENCH_ROUTE
      },
      {
        id: 'go-site-shield',
        title: 'Site Shield',
        caption: 'Inspect the active route and browser guardrails.',
        kind: 'navigate' as const,
        target: WATERFALL_SITE_SHIELD_ROUTE
      },
      {
        id: 'go-privacy-auditor',
        title: 'Privacy Auditor',
        caption: 'Inspect bridge health and privacy posture.',
        kind: 'navigate' as const,
        target: WATERFALL_PRIVACY_AUDITOR_ROUTE
      },
      {
        id: 'go-security-architect',
        title: 'Security Architect',
        caption: 'Inspect toolkit inventory and bounty export.',
        kind: 'navigate' as const,
        target: WATERFALL_SECURITY_ARCHITECT_ROUTE
      },
      {
        id: 'go-updates',
        title: 'Update Deck',
        caption: 'Inspect signed manifests, staged artifacts, and rollback posture.',
        kind: 'navigate' as const,
        target: WATERFALL_UPDATES_ROUTE
      },
      {
        id: 'go-settings',
        title: 'Native Settings',
        caption: 'Open the native settings snapshot.',
        kind: 'navigate' as const,
        target: 'waterfall://settings'
      },
      {
        id: 'refresh-native',
        title: 'Refresh Route',
        caption: 'Ask the native renderer for a fresh pass.',
        kind: 'refresh' as const
      }
    ];
    const homeAndSearchRouteActions = staticRouteActions.filter(
      (action) => action.id === 'go-home' || action.id === 'go-search'
    );

    const searchRoutes = Array.from(
      new Set([
        WATERFALL_SEARCH_ROUTE,
        ...tabs
          .map((tab) => tab.url)
          .filter((route): route is string => Boolean(route) && isWaterfallSearchRoute(route))
          .map((route) => normalizeWaterfallRoute(route))
      ])
    );

    searchRoutes.forEach((route) => {
      const searchQuery = getWaterfallSearchQuery(route);
      const searchState = searchRouteStates[route];
      const response = searchState?.response;

      actions[route] = [
        {
          id: 'search-clear',
          title: 'Clear Search Deck',
          caption: 'Open a blank WaterFall search route.',
          kind: 'navigate',
          target: WATERFALL_SEARCH_ROUTE
        },
        ...(response?.results.slice(0, 6).map((result, index) => ({
          id: `search-result-${index}`,
          title: result.title,
          caption: `${result.provider} | ${(result.relevanceScore * 100).toFixed(0)}%`,
          kind: 'navigate' as const,
          target: result.url
        })) || []),
        {
          id: 'search-settings',
          title: 'Settings Snapshot',
          caption: 'Adjust native search lane preferences.',
          kind: 'navigate',
          target: 'waterfall://settings'
        },
        {
          id: 'search-home',
          title: 'Native Home',
          caption: 'Return to the WaterFall dashboard.',
          kind: 'navigate',
          target: WATERFALL_HOME_ROUTE
        },
        {
          id: 'search-routes',
          title: 'Route Atlas',
          caption: 'Survey the native route network.',
          kind: 'navigate',
          target: 'waterfall://routes'
        },
        {
          id: 'search-refresh',
          title: searchQuery ? `Refresh | ${searchQuery}` : 'Refresh Search',
          caption: 'Ask WaterFall for a fresh native search pass.',
          kind: 'refresh'
        }
      ];
    });

    actions['waterfall://home'] = [
      ...staticRouteActions,
      {
        id: 'create-tab-launchpad',
        title: 'Open Launch Pad Tab',
        caption: 'Create a fresh blank WaterFall tab.',
        kind: 'create-tab'
      },
      {
        id: 'create-tab-homepage',
        title: 'Open Home Page Tab',
        caption: settings.homePage,
        kind: 'create-tab',
        target: settings.homePage
      },
      {
        id: 'create-tab-search',
        title: 'Open Search Deck',
        caption: 'Create a fresh native WaterFall search tab.',
        kind: 'create-tab',
        target: WATERFALL_SEARCH_ROUTE
      },
      {
        id: 'toggle-active-bookmark',
        title: bookmarked ? 'Unpin Active Route' : 'Pin Active Route',
        caption: activeTab.url || 'No active route is available to bookmark.',
        kind: 'toggle-bookmark',
        target: activeTab.url || 'waterfall://home'
      },
      {
        id: 'go-session',
        title: 'Session Deck',
        caption: 'See open tabs and current session memory.',
        kind: 'navigate',
        target: 'waterfall://session'
      },
      {
        id: 'go-routes',
        title: 'Route Atlas',
        caption: 'Browse the native route index.',
        kind: 'navigate',
        target: 'waterfall://routes'
      }
    ];

    actions['waterfall://history'] = [
      ...history.slice(0, 8).map((entry, index) => ({
        id: `history-${index}`,
        title: entry.title,
        caption: entry.url,
        kind: 'navigate' as const,
        target: entry.url
      })),
      {
        id: 'clear-history',
        title: 'Clear History Deck',
        caption: 'Wipe the current native history memory.',
        kind: 'clear-history'
      },
      {
        id: 'create-tab-launchpad',
        title: 'Open Launch Pad Tab',
        caption: 'Create a fresh blank WaterFall tab.',
        kind: 'create-tab'
      },
      ...homeAndSearchRouteActions
    ];

    actions['waterfall://bookmarks'] = [
      ...bookmarks.slice(0, 8).map((bookmark, index) => ({
        id: `bookmark-${index}`,
        title: bookmark.title,
        caption: bookmark.url,
        kind: 'navigate' as const,
        target: bookmark.url
      })),
      ...homeAndSearchRouteActions
    ];

    actions['waterfall://downloads'] = [
      ...downloads.slice(0, 8).map((download, index) => ({
        id: `download-${index}`,
        title: download.filename,
        caption: `${download.status} | ${formatKilobytes(download.receivedBytes)} of ${formatKilobytes(download.totalBytes)}`,
        kind: 'show-download' as const,
        filePath: download.filePath
      })),
      ...homeAndSearchRouteActions
    ];

    actions[WATERFALL_SECURITY_WORKBENCH_ROUTE] = [
      {
        id: 'export-security-report',
        title: 'Export Security Report',
        caption: 'Write the current security workbench state to a local evidence report.',
        kind: 'export-security-report'
      },
      ...downloads.slice(0, 8).map((download) => ({
        id: download.securityScan?.quarantined
          ? `release-quarantine-${download.id}`
          : `scan-download-${download.id}`,
        title: download.securityScan?.quarantined
          ? `Release ${download.filename}`
          : `Rescan ${download.filename}`,
        caption: download.securityScan?.quarantined
          ? 'Move the quarantined artifact back into the local downloads folder.'
          : 'Run Download Gate against the current artifact state again.',
        kind: download.securityScan?.quarantined
          ? ('release-download-quarantine' as const)
          : ('scan-download' as const),
        downloadId: download.id
      })),
      {
        id: 'security-workbench-downloads',
        title: 'Download Hangar',
        caption: 'Open the raw download deck.',
        kind: 'navigate',
        target: 'waterfall://downloads'
      },
      {
        id: 'security-workbench-proof',
        title: 'Security Proof',
        caption: 'Inspect validation, threat posture, and implementation evidence.',
        kind: 'navigate',
        target: 'waterfall://security-proof'
      },
      ...homeAndSearchRouteActions
    ];

    actions[WATERFALL_SITE_SHIELD_ROUTE] = [
      {
        id: 'site-shield-settings',
        title: 'Settings Snapshot',
        caption: 'Adjust browser guardrails and route protections.',
        kind: 'navigate',
        target: 'waterfall://settings'
      },
      {
        id: 'site-shield-workbench',
        title: 'Security Workbench',
        caption: 'Inspect scans, quarantine posture, and evidence export.',
        kind: 'navigate',
        target: WATERFALL_SECURITY_WORKBENCH_ROUTE
      },
      {
        id: 'site-shield-refresh',
        title: 'Refresh Route',
        caption: 'Recompute active route posture.',
        kind: 'refresh'
      },
      ...homeAndSearchRouteActions
    ];

    actions[WATERFALL_PRIVACY_AUDITOR_ROUTE] = [
      {
        id: securityStatus?.vpnEnabled ? 'auditor-disable-vpn' : 'auditor-enable-vpn',
        title: securityStatus?.vpnEnabled ? 'Disable Sovereign VPN' : 'Enable Sovereign VPN',
        caption: securityStatus?.vpnEnabled
          ? 'Ask the bridge to stand the built-in VPN lane down.'
          : 'Ask the bridge to raise the built-in VPN lane.',
        kind: securityStatus?.vpnEnabled ? 'disable-vpn' : 'enable-vpn'
      },
      {
        id: 'auditor-export-report',
        title: 'Export Security Report',
        caption: 'Write the current privacy and security posture to local evidence.',
        kind: 'export-security-report'
      },
      {
        id: 'auditor-updates',
        title: 'Update Deck',
        caption: 'Inspect signed update verification and rollback posture.',
        kind: 'navigate',
        target: WATERFALL_UPDATES_ROUTE
      },
      {
        id: 'auditor-workbench',
        title: 'Security Workbench',
        caption: 'Operate Download Gate and quarantine lanes.',
        kind: 'navigate',
        target: WATERFALL_SECURITY_WORKBENCH_ROUTE
      },
      ...homeAndSearchRouteActions
    ];

    actions[WATERFALL_SECURITY_ARCHITECT_ROUTE] = [
      {
        id: 'architect-export-bounty-pack',
        title: 'Export Bounty Pack',
        caption: 'Write markdown and JSON evidence bundles for review or bounty submission.',
        kind: 'export-bounty-pack'
      },
      {
        id: 'architect-export-report',
        title: 'Export Security Report',
        caption: 'Write the current workbench posture to local evidence.',
        kind: 'export-security-report'
      },
      {
        id: 'architect-workbench',
        title: 'Security Workbench',
        caption: 'Operate Download Gate and quarantine posture.',
        kind: 'navigate',
        target: WATERFALL_SECURITY_WORKBENCH_ROUTE
      },
      {
        id: 'architect-auditor',
        title: 'Privacy Auditor',
        caption: 'Review bridge health and browser exposure posture.',
        kind: 'navigate',
        target: WATERFALL_PRIVACY_AUDITOR_ROUTE
      },
      ...homeAndSearchRouteActions
    ];

    actions[WATERFALL_UPDATES_ROUTE] = [
      {
        id: 'check-updates',
        title: updatesLoading ? 'Checking Updates' : 'Check Signed Manifest',
        caption: updatesLoading
          ? 'WaterFall is refreshing the release manifest now.'
          : 'Refresh manifest verification and staging posture.',
        kind: 'check-updates'
      },
      {
        id: 'apply-update',
        title:
          updateManifestReady
            ? `Stage Update ${updateManifest?.version || ''}`
            : 'Stage Verified Update',
        caption:
          updateManifestReady
            ? 'Stage the verified artifact locally and capture rollback metadata.'
            : 'WaterFall will only stage a manifest after it verifies.',
        kind: 'apply-update'
      },
      {
        id: 'updates-settings',
        title: 'Settings Snapshot',
        caption: 'Open browser settings and backup controls.',
        kind: 'navigate',
        target: 'waterfall://settings'
      },
      {
        id: 'updates-proof',
        title: 'Security Proof',
        caption: 'Inspect verification and validation surfaces.',
        kind: 'navigate',
        target: 'waterfall://security-proof'
      },
      ...homeAndSearchRouteActions
    ];

    actions['waterfall://settings'] = [
      {
        id: 'open-settings',
        title: 'Open Drawer',
        caption: 'Open WaterFall settings drawer for direct controls.',
        kind: 'open-settings'
      },
      {
        id: 'copy-node',
        title: 'Copy Node ID',
        caption: 'Copy WaterFall mesh identity to the clipboard.',
        kind: 'copy-node-id'
      },
      {
        id: 'set-home-search',
        title: 'Set Home To Native Search',
        caption: 'Use waterfall://search as the browser home page.',
        kind: 'set-setting',
        settingPath: 'homePage',
        stringValue: WATERFALL_SEARCH_ROUTE
      },
      {
        id: 'toggle-restore-session',
        title: `Restore Session ${settings.restoreSession ? 'On' : 'Off'}`,
        caption: 'Toggle whether WaterFall restores the last session on launch.',
        kind: 'toggle-setting',
        settingPath: 'restoreSession'
      },
      {
        id: 'set-home-native',
        title: 'Set Home To Native Home',
        caption: 'Use waterfall://home as the browser home page.',
        kind: 'set-setting',
        settingPath: 'homePage',
        stringValue: 'waterfall://home'
      },
      {
        id: 'set-home-duckduckgo',
        title: 'Set Home To DuckDuckGo',
        caption: 'Use https://duckduckgo.com as the browser home page.',
        kind: 'set-setting',
        settingPath: 'homePage',
        stringValue: 'https://duckduckgo.com'
      },
      {
        id: 'set-home-startpage',
        title: 'Set Home To Startpage',
        caption: 'Use https://www.startpage.com as the browser home page.',
        kind: 'set-setting',
        settingPath: 'homePage',
        stringValue: 'https://www.startpage.com'
      },
      {
        id: 'set-search-duckduckgo',
        title: 'Search Engine DuckDuckGo',
        caption: 'Make DuckDuckGo the lead provider lane for native WaterFall search.',
        kind: 'set-setting',
        settingPath: 'searchEngine',
        stringValue: 'duckduckgo'
      },
      {
        id: 'set-search-startpage',
        title: 'Search Engine Startpage',
        caption: 'Make Startpage the lead provider lane for native WaterFall search.',
        kind: 'set-setting',
        settingPath: 'searchEngine',
        stringValue: 'startpage'
      },
      {
        id: 'set-search-kagi',
        title: 'Search Engine Kagi',
        caption: 'Make Kagi the lead provider lane for native WaterFall search.',
        kind: 'set-setting',
        settingPath: 'searchEngine',
        stringValue: 'kagi'
      },
      {
        id: 'toggle-dnt',
        title: `Do Not Track ${settings.privacy.doNotTrack ? 'On' : 'Off'}`,
        caption: 'Toggle the DNT request header.',
        kind: 'toggle-setting',
        settingPath: 'privacy.doNotTrack'
      },
      {
        id: 'toggle-gpc',
        title: `Global Privacy Control ${settings.privacy.globalPrivacyControl ? 'On' : 'Off'}`,
        caption: 'Toggle GPC headers.',
        kind: 'toggle-setting',
        settingPath: 'privacy.globalPrivacyControl'
      },
      {
        id: 'toggle-https-only',
        title: `HTTPS Upgrades ${settings.privacy.httpsOnlyMode ? 'On' : 'Off'}`,
        caption: 'Toggle automatic public-route upgrades to https.',
        kind: 'toggle-setting',
        settingPath: 'privacy.httpsOnlyMode'
      },
      {
        id: 'toggle-block-trackers',
        title: `Tracker Blocking ${settings.privacy.blockTrackers ? 'On' : 'Off'}`,
        caption: 'Toggle the tracker block list.',
        kind: 'toggle-setting',
        settingPath: 'privacy.blockTrackers'
      },
      {
        id: 'toggle-kill-switch',
        title: `Master Kill Switch ${settings.privacy.masterKillSwitch ? 'Armed' : 'Idle'}`,
        caption: 'Block every outgoing web request in the WaterFall browser partition instantly.',
        kind: 'toggle-setting',
        settingPath: 'privacy.masterKillSwitch'
      },
      {
        id: 'toggle-permissions-lockdown',
        title: `Permissions Lockdown ${settings.privacy.permissionsLockdown ? 'On' : 'Off'}`,
        caption: 'Control whether guest permission prompts are denied by default.',
        kind: 'toggle-setting',
        settingPath: 'privacy.permissionsLockdown'
      },
      {
        id: 'toggle-strip-referrers',
        title: `Strip Referrers ${settings.privacy.stripReferrers ? 'On' : 'Off'}`,
        caption: 'Remove referrer headers from guest web traffic.',
        kind: 'toggle-setting',
        settingPath: 'privacy.stripReferrers'
      },
      {
        id: 'toggle-anti-fingerprinting',
        title: `Anti-Fingerprinting ${settings.privacy.antiFingerprinting ? 'On' : 'Off'}`,
        caption: 'Shape outgoing browser headers to reduce passive fingerprinting.',
        kind: 'toggle-setting',
        settingPath: 'privacy.antiFingerprinting'
      },
      {
        id: 'toggle-block-popups',
        title: `Popup Blocker ${settings.privacy.blockPopups ? 'On' : 'Off'}`,
        caption: 'Block or externally hand off guest popup attempts.',
        kind: 'toggle-setting',
        settingPath: 'privacy.blockPopups'
      },
      {
        id: 'toggle-scan-downloads-on-start',
        title: `Preflight Scans ${settings.security.scanDownloadsOnStart ? 'On' : 'Off'}`,
        caption: 'Toggle download gate checks before files are written to disk.',
        kind: 'toggle-setting',
        settingPath: 'security.scanDownloadsOnStart'
      },
      {
        id: 'toggle-scan-downloads-on-completion',
        title: `Postflight Scans ${settings.security.scanDownloadsOnCompletion ? 'On' : 'Off'}`,
        caption: 'Toggle download gate checks after files complete.',
        kind: 'toggle-setting',
        settingPath: 'security.scanDownloadsOnCompletion'
      },
      {
        id: 'toggle-quarantine-high-risk-downloads',
        title: `Quarantine High-Risk ${settings.security.quarantineHighRiskDownloads ? 'On' : 'Off'}`,
        caption: 'Toggle automatic quarantine for risky downloads.',
        kind: 'toggle-setting',
        settingPath: 'security.quarantineHighRiskDownloads'
      },
      {
        id: 'toggle-native-artifact-scanning',
        title: `Native Artifact Scanning ${settings.security.nativeArtifactScanning ? 'On' : 'Off'}`,
        caption: 'Toggle local artifact inspection inside the browser shell.',
        kind: 'toggle-setting',
        settingPath: 'security.nativeArtifactScanning'
      },
      {
        id: 'toggle-external-authorized-scanning',
        title: `Authorized External Scanning ${settings.security.externalAuthorizedScanning ? 'On' : 'Off'}`,
        caption: 'Toggle support for explicitly authorized external target flows.',
        kind: 'toggle-setting',
        settingPath: 'security.externalAuthorizedScanning'
      },
      {
        id: 'toggle-export-evidence-bundles',
        title: `Evidence Export ${settings.security.exportEvidenceBundles ? 'On' : 'Off'}`,
        caption: 'Toggle exportable evidence bundles from the security workbench.',
        kind: 'toggle-setting',
        settingPath: 'security.exportEvidenceBundles'
      },
      {
        id: 'go-collective',
        title: 'Collective Deck',
        caption: 'Open native collective controls snapshot.',
        kind: 'navigate',
        target: 'waterfall://collective'
      },
      {
        id: 'go-security-workbench',
        title: 'Security Workbench',
        caption: 'Inspect scans, quarantine posture, and evidence export.',
        kind: 'navigate',
        target: WATERFALL_SECURITY_WORKBENCH_ROUTE
      },
      {
        id: 'go-updates',
        title: 'Update Deck',
        caption: 'Inspect signed manifests, staged artifacts, and rollback posture.',
        kind: 'navigate',
        target: WATERFALL_UPDATES_ROUTE
      },
      {
        id: 'go-extensions',
        title: 'Extension Deck',
        caption: 'Open native extension readout.',
        kind: 'navigate',
        target: 'waterfall://extensions'
      },
      {
        id: 'go-orchestrator',
        title: 'Orchestrator Deck',
        caption: 'Open the privacy-first architecture map.',
        kind: 'navigate',
        target: 'waterfall://orchestrator'
      },
      {
        id: 'go-security-proof',
        title: 'Security Proof',
        caption: 'Open the threat model and validation surface.',
        kind: 'navigate',
        target: 'waterfall://security-proof'
      }
    ];

    actions['waterfall://session'] = [
      ...tabs.slice(0, 8).map((tab, index) => ({
        id: `session-tab-${index}`,
        title: tab.title,
        caption: tab.url || 'waterfall://home',
        kind: 'navigate' as const,
        target: tab.url || 'waterfall://home'
      })),
      {
        id: 'create-tab-launchpad',
        title: 'Open Launch Pad Tab',
        caption: 'Create a fresh blank WaterFall tab.',
        kind: 'create-tab'
      },
      {
        id: 'create-tab-home',
        title: 'Open Native Home Tab',
        caption: 'Create a new waterfall://home tab.',
        kind: 'create-tab',
        target: 'waterfall://home'
      },
      {
        id: 'duplicate-active-tab',
        title: 'Duplicate Active Route',
        caption: activeTab.url || settings.homePage,
        kind: 'create-tab',
        target: activeTab.url || settings.homePage
      },
      {
        id: 'clear-history',
        title: 'Clear History Deck',
        caption: 'Drop route memory while keeping current tabs.',
        kind: 'clear-history'
      },
      {
        id: 'reset-session',
        title: 'Reset Session',
        caption: 'Reopen a fresh launch pad and clear transient session state.',
        kind: 'reset-session'
      }
    ];

    actions['waterfall://extensions'] = [
      ...extensions.slice(0, 8).map((extension, index) => ({
        id: `extension-${index}`,
        title: extension.name,
        caption: extension.loadError || extension.path,
        kind: 'remove-extension' as const,
        extensionPath: extension.path
      })),
      {
        id: 'add-extension',
        title: 'Add Trusted Extension',
        caption: 'Open the unpacked extension picker.',
        kind: 'add-extension'
      },
      {
        id: 'open-extension-settings',
        title: 'Open Settings Drawer',
        caption: 'Manage unpacked extensions from the settings deck.',
        kind: 'open-settings'
      }
    ];

    actions['waterfall://collective'] = [
      {
        id: 'toggle-collective-enabled',
        title: `Collective Mesh ${settings.collective.enabled ? 'On' : 'Off'}`,
        caption: 'Toggle participation in the future shared-compute mesh.',
        kind: 'toggle-setting',
        settingPath: 'collective.enabled'
      },
      {
        id: 'toggle-collective-cpu',
        title: `CPU Sharing ${settings.collective.cpuEnabled ? 'On' : 'Off'}`,
        caption: 'Toggle CPU contribution to the collective.',
        kind: 'toggle-setting',
        settingPath: 'collective.cpuEnabled'
      },
      {
        id: 'toggle-collective-gpu',
        title: `GPU Sharing ${settings.collective.gpuEnabled ? 'On' : 'Off'}`,
        caption: 'Toggle GPU contribution to the collective.',
        kind: 'toggle-setting',
        settingPath: 'collective.gpuEnabled'
      },
      {
        id: 'cpu-cap-down',
        title: `CPU Cap ${settings.collective.cpuLimitPercent}%`,
        caption: 'Reduce the CPU pledge cap by 5 percent.',
        kind: 'set-setting',
        settingPath: 'collective.cpuLimitPercent',
        numberValue: settings.collective.cpuLimitPercent - 5
      },
      {
        id: 'cpu-cap-up',
        title: `CPU Cap ${settings.collective.cpuLimitPercent}%`,
        caption: 'Increase the CPU pledge cap by 5 percent.',
        kind: 'set-setting',
        settingPath: 'collective.cpuLimitPercent',
        numberValue: settings.collective.cpuLimitPercent + 5
      },
      {
        id: 'gpu-cap-down',
        title: `GPU Cap ${settings.collective.gpuLimitPercent}%`,
        caption: 'Reduce the GPU pledge cap by 5 percent.',
        kind: 'set-setting',
        settingPath: 'collective.gpuLimitPercent',
        numberValue: settings.collective.gpuLimitPercent - 5
      },
      {
        id: 'gpu-cap-up',
        title: `GPU Cap ${settings.collective.gpuLimitPercent}%`,
        caption: 'Increase the GPU pledge cap by 5 percent.',
        kind: 'set-setting',
        settingPath: 'collective.gpuLimitPercent',
        numberValue: settings.collective.gpuLimitPercent + 5
      },
      {
        id: 'session-cap-down',
        title: `Session Cap ${settings.collective.sessionCapMinutes} min`,
        caption: 'Lower the collective session cap by 5 minutes.',
        kind: 'set-setting',
        settingPath: 'collective.sessionCapMinutes',
        numberValue: settings.collective.sessionCapMinutes - 5
      },
      {
        id: 'session-cap-up',
        title: `Session Cap ${settings.collective.sessionCapMinutes} min`,
        caption: 'Raise the collective session cap by 5 minutes.',
        kind: 'set-setting',
        settingPath: 'collective.sessionCapMinutes',
        numberValue: settings.collective.sessionCapMinutes + 5
      },
      {
        id: 'collective-settings',
        title: 'Open Settings Drawer',
        caption: 'Tune CPU, GPU, and collective consent controls.',
        kind: 'open-settings'
      },
      {
        id: 'go-mesh',
        title: 'Mesh Deck',
        caption: 'Open trust and peer identity page.',
        kind: 'navigate',
        target: 'waterfall://mesh'
      },
      {
        id: 'refresh-collective',
        title: 'Refresh Route',
        caption: 'Recompute the current pledge snapshot.',
        kind: 'refresh'
      }
    ];

    actions['waterfall://mesh'] = [
      {
        id: 'mesh-settings',
        title: 'Open Settings Drawer',
        caption: 'Adjust profile identity and future mesh consent.',
        kind: 'open-settings'
      },
      {
        id: 'mesh-copy-node',
        title: 'Copy Node ID',
        caption: settings.account.nodeId,
        kind: 'copy-node-id'
      },
      {
        id: 'mesh-collective',
        title: 'Collective Deck',
        caption: 'Open the collective acceleration page.',
        kind: 'navigate',
        target: 'waterfall://collective'
      }
    ];

    actions['waterfall://engine-lab'] = [
      {
        id: 'lab-home',
        title: 'Native Home',
        caption: 'Return to the native dashboard.',
        kind: 'navigate',
        target: 'waterfall://home'
      },
      {
        id: 'lab-routes',
        title: 'Route Atlas',
        caption: 'See the available native pages.',
        kind: 'navigate',
        target: 'waterfall://routes'
      },
      {
        id: 'lab-refresh',
        title: 'Refresh Route',
        caption: 'Run another engine-lab render pass.',
        kind: 'refresh'
      }
    ];

    actions['waterfall://routes'] = [
      {
        id: 'atlas-home',
        title: 'Native Home',
        caption: 'Return to the WaterFall dashboard.',
        kind: 'navigate',
        target: 'waterfall://home'
      },
      {
        id: 'atlas-engine',
        title: 'Engine Lab',
        caption: 'Open the native engine lab route.',
        kind: 'navigate',
        target: 'waterfall://engine-lab'
      },
      {
        id: 'atlas-session',
        title: 'Session Deck',
        caption: 'Open live tab/session state.',
        kind: 'navigate',
        target: 'waterfall://session'
      },
      {
        id: 'atlas-settings',
        title: 'Settings Snapshot',
        caption: 'Open the first-party settings readout.',
        kind: 'navigate',
        target: 'waterfall://settings'
      },
      {
        id: 'atlas-orchestrator',
        title: 'Orchestrator Deck',
        caption: 'Open the privacy-first architecture map.',
        kind: 'navigate',
        target: 'waterfall://orchestrator'
      },
      {
        id: 'atlas-proof',
        title: 'Security Proof',
        caption: 'Open the security and validation surface.',
        kind: 'navigate',
        target: 'waterfall://security-proof'
      }
    ];

    actions['waterfall://orchestrator'] = [
      {
        id: 'orchestrator-settings',
        title: 'Settings Snapshot',
        caption: 'Open the live browser settings surface.',
        kind: 'navigate',
        target: 'waterfall://settings'
      },
      {
        id: 'orchestrator-privacy',
        title: 'Privacy Fortress',
        caption: 'Open use cases and privacy posture.',
        kind: 'navigate',
        target: 'waterfall://privacy-fortress'
      },
      {
        id: 'orchestrator-proof',
        title: 'Security Proof',
        caption: 'Open validation and implementation evidence.',
        kind: 'navigate',
        target: 'waterfall://security-proof'
      },
      {
        id: 'orchestrator-workbench',
        title: 'Security Workbench',
        caption: 'Operate download scans, quarantine, and evidence export.',
        kind: 'navigate',
        target: WATERFALL_SECURITY_WORKBENCH_ROUTE
      },
      {
        id: 'orchestrator-refresh',
        title: 'Refresh Route',
        caption: 'Run another orchestrator render pass.',
        kind: 'refresh'
      }
    ];

    actions['waterfall://privacy-fortress'] = [
      {
        id: 'fortress-settings',
        title: 'Settings Snapshot',
        caption: 'Open live privacy and browser controls.',
        kind: 'navigate',
        target: 'waterfall://settings'
      },
      {
        id: 'fortress-orchestrator',
        title: 'Orchestrator Deck',
        caption: 'Open the system architecture map.',
        kind: 'navigate',
        target: 'waterfall://orchestrator'
      },
      {
        id: 'fortress-proof',
        title: 'Security Proof',
        caption: 'Open the validation and proof surface.',
        kind: 'navigate',
        target: 'waterfall://security-proof'
      },
      {
        id: 'fortress-refresh',
        title: 'Refresh Route',
        caption: 'Run another privacy-fortress render pass.',
        kind: 'refresh'
      }
    ];

    actions['waterfall://security-proof'] = [
      {
        id: 'proof-settings',
        title: 'Settings Snapshot',
        caption: 'Open live browser settings.',
        kind: 'navigate',
        target: 'waterfall://settings'
      },
      {
        id: 'proof-orchestrator',
        title: 'Orchestrator Deck',
        caption: 'Open the architecture map.',
        kind: 'navigate',
        target: 'waterfall://orchestrator'
      },
      {
        id: 'proof-fortress',
        title: 'Privacy Fortress',
        caption: 'Open privacy use cases and posture.',
        kind: 'navigate',
        target: 'waterfall://privacy-fortress'
      },
      {
        id: 'proof-workbench',
        title: 'Security Workbench',
        caption: 'Operate download scanning and evidence export.',
        kind: 'navigate',
        target: WATERFALL_SECURITY_WORKBENCH_ROUTE
      },
      {
        id: 'proof-refresh',
        title: 'Refresh Route',
        caption: 'Run another proof-surface render pass.',
        kind: 'refresh'
      }
    ];

    return actions;
  }, [
    activeTab.url,
    bookmarks,
    bookmarked,
    downloads,
    extensions,
    history,
    settings.account.nodeId,
    settings.collective.cpuEnabled,
    settings.collective.enabled,
    settings.collective.cpuLimitPercent,
    settings.collective.gpuEnabled,
    settings.collective.gpuLimitPercent,
    settings.collective.sessionCapMinutes,
    settings.homePage,
    settings.privacy.blockTrackers,
    settings.privacy.doNotTrack,
    settings.privacy.globalPrivacyControl,
    settings.privacy.httpsOnlyMode,
    settings.security.exportEvidenceBundles,
    settings.security.externalAuthorizedScanning,
    settings.security.nativeArtifactScanning,
    settings.security.quarantineHighRiskDownloads,
    settings.security.scanDownloadsOnCompletion,
    settings.security.scanDownloadsOnStart,
    settings.security.strictScopeMode,
    settings.restoreSession,
    settings.searchEngine,
    securityStatus?.vpnEnabled,
    searchRouteStates,
    tabs,
    updateManifest,
    updatesLoading
  ]);

  useEffect(() => {
    const electronApi = window.electron;
    if (!electronApi) {
      setBrowserNotice('WaterFall must run inside the local Electron shell.');
      return;
    }

    let active = true;

    const bootstrap = async () => {
      try {
        const [storedSettings, storedSession, nextResourceProfile, nextDownloads, nextExtensions] =
          await Promise.all([
          electronApi.store.get<WaterfallBrowserSettings>(WATERFALL_SETTINGS_KEY),
          electronApi.store.get<WaterfallBrowserSession>(WATERFALL_SESSION_KEY),
          electronApi.system.getResourceProfile(),
          electronApi.browser.getDownloads(),
          electronApi.browser.getExtensions()
          ]);

        if (!active) {
          return;
        }

        const nextSettings = sanitizeSettings(storedSettings);
        const nextSession = sanitizeSession(storedSession);
        const freshSession = nextSettings.restoreSession ? nextSession : createDefaultSession();

        setSettings(nextSettings);
        setSettingsHomeDraft(nextSettings.homePage);
        setResourceProfile(nextResourceProfile);
        setDownloads(nextDownloads);
        setExtensions(nextExtensions);
        setTabs(freshSession.tabs);
        setNativeRouteTimelines(seedNativeRouteTimelines(freshSession.tabs));
        setActiveTabId(freshSession.activeTabId);
        setBookmarks(nextSession.bookmarks);
        setHistory(nextSession.history);
        setAddressDraft(freshSession.tabs[0]?.url || '');
      } catch (error) {
        if (!active) {
          return;
        }

        setBrowserNotice(
          error instanceof Error
            ? error.message
            : 'WaterFall could not restore its local session.'
        );
      } finally {
        if (active) {
          setBootstrapped(true);
        }
      }
    };

    void bootstrap();

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!addressFocused) {
      setAddressDraft(activeTab.url || '');
    }
  }, [activeTab.id, activeTab.url, addressFocused]);

  useEffect(() => {
    setSettingsHomeDraft(settings.homePage);
  }, [settings.homePage]);

  useEffect(() => {
    if (!window.electron || !bootstrapped) {
      return;
    }

    void window.electron.store.set(WATERFALL_SETTINGS_KEY, settings);
  }, [bootstrapped, settings]);

  useEffect(() => {
    if (!bootstrapped || !window.waterfall?.updates) {
      return;
    }

    void refreshUpdateManifest(true);
  }, [bootstrapped, refreshUpdateManifest]);

  useEffect(() => {
    if (!bootstrapped || !window.waterfall?.security) {
      return;
    }

    void refreshSecurityStatus(true);
  }, [bootstrapped, refreshSecurityStatus]);

  useEffect(() => {
    if (!bootstrapped || !window.waterfall?.orchestrator) {
      return;
    }

    void refreshBridgeHealth(true);
  }, [bootstrapped, refreshBridgeHealth]);

  useEffect(() => {
    if (!bootstrapped || !window.electron?.browser) {
      return;
    }

    void refreshSecurityToolkitInventory(true);
  }, [bootstrapped, refreshSecurityToolkitInventory]);

  useEffect(() => {
    if (!window.electron || !bootstrapped) {
      return;
    }

    void window.electron.browser.applySettings(settings).catch((error) => {
      setBrowserNotice(
        error instanceof Error ? error.message : 'WaterFall could not apply runtime settings.'
      );
    });
  }, [bootstrapped, settings]);

  useEffect(() => {
    if (!window.electron || !bootstrapped) {
      return;
    }

    void window.electron.store.set(WATERFALL_SESSION_KEY, {
      tabs,
      activeTabId,
      bookmarks,
      history
    } satisfies WaterfallBrowserSession);
  }, [activeTabId, bookmarks, bootstrapped, history, tabs]);

  useEffect(() => {
    if (!window.electron) {
      return;
    }

    return window.electron.browser.onDownloadUpdated((download) => {
      setDownloads((current) => {
        const nextDownloads = current.filter((entry) => entry.id !== download.id);
        return [download, ...nextDownloads].sort((left, right) => right.startedAt - left.startedAt);
      });
    });
  }, []);

  useEffect(() => {
    const handleShortcuts = (event: KeyboardEvent) => {
      const commandPressed = event.ctrlKey || event.metaKey;
      const normalizedKey = event.key.toLowerCase();

      if (commandPressed && normalizedKey === 'l') {
        event.preventDefault();
        addressInputRef.current?.focus();
        addressInputRef.current?.select();
      }

      if (commandPressed && normalizedKey === 't') {
        event.preventDefault();
        const nextTab = createBlankTab();
        setTabs((current) => [...current, nextTab]);
        setActiveTabId(nextTab.id);
      }

      if (commandPressed && normalizedKey === 'w') {
        event.preventDefault();
        handleCloseTab(activeTab.id);
      }

      if (
        event.altKey &&
        event.key === 'ArrowLeft' &&
        ((activeTabIsInternalRoute && activeTab.canGoBack) || activeWebview?.canGoBack())
      ) {
        event.preventDefault();
        handleGoBackActiveTab();
      }

      if (
        event.altKey &&
        event.key === 'ArrowRight' &&
        ((activeTabIsInternalRoute && activeTab.canGoForward) || activeWebview?.canGoForward())
      ) {
        event.preventDefault();
        handleGoForwardActiveTab();
      }
    };

    window.addEventListener('keydown', handleShortcuts);
    return () => window.removeEventListener('keydown', handleShortcuts);
  }, [
    activeTab.canGoBack,
    activeTab.canGoForward,
    activeTab.id,
    activeTabIsInternalRoute,
    activeWebview
  ]);

  const handleTabChange = useCallback((tabId: string, patch: Partial<WaterfallTabState>) => {
    setTabs((current) =>
      current.map((tab) => (tab.id === tabId ? { ...tab, ...patch } : tab))
    );
  }, []);

  const handleHistoryEntry = useCallback((entry: WaterfallHistoryEntry) => {
    setHistory((current) => dedupeHistory([entry, ...current]).slice(0, 36));
  }, []);

  const handleNodeChange = useCallback((tabId: string, node: Electron.WebviewTag | null) => {
    webviewNodes.current[tabId] = node;
  }, []);

  const getNativeRouteTimeline = (tabId: string) =>
    nativeRouteTimelines[tabId] || {
      entries: [],
      index: -1
    };

  const updateNativeRouteTimeline = (
    tabId: string,
    nextRoute: string,
    mode: 'push' | 'replace'
  ) => {
    const normalizedRoute = normalizeWaterfallRoute(nextRoute);
    let nextTimeline: WaterfallNativeRouteTimeline = {
      entries: [normalizedRoute],
      index: 0
    };

    setNativeRouteTimelines((current) => {
      const existingTimeline = current[tabId];

      if (mode === 'replace' && existingTimeline) {
        const nextEntries = [...existingTimeline.entries];
        if (existingTimeline.index >= 0 && existingTimeline.index < nextEntries.length) {
          nextEntries[existingTimeline.index] = normalizedRoute;
        } else {
          nextEntries.push(normalizedRoute);
        }
        nextTimeline = {
          entries: nextEntries,
          index:
            existingTimeline.index >= 0
              ? Math.min(existingTimeline.index, nextEntries.length - 1)
              : nextEntries.length - 1
        };

        return {
          ...current,
          [tabId]: nextTimeline
        };
      }

      if (!existingTimeline) {
        nextTimeline = {
          entries: [normalizedRoute],
          index: 0
        };
        return {
          ...current,
          [tabId]: nextTimeline
        };
      }

      const visibleEntries = existingTimeline.entries.slice(0, existingTimeline.index + 1);
      if (visibleEntries[visibleEntries.length - 1] === normalizedRoute) {
        nextTimeline = existingTimeline;
        return current;
      }

      nextTimeline = {
        entries: [...visibleEntries, normalizedRoute],
        index: visibleEntries.length
      };

      return {
        ...current,
        [tabId]: nextTimeline
      };
    });

    return nextTimeline;
  };

  const syncNativeRouteNavigationState = (
    tabId: string,
    route: string,
    mode: 'push' | 'replace' = 'push'
  ) => {
    const timeline = updateNativeRouteTimeline(tabId, route, mode);
    return {
      canGoBack: timeline.index > 0,
      canGoForward: timeline.index >= 0 && timeline.index < timeline.entries.length - 1
    };
  };

  const navigateNativeHistory = (direction: 'back' | 'forward') => {
    const timeline = getNativeRouteTimeline(activeTab.id);
    const nextIndex = direction === 'back' ? timeline.index - 1 : timeline.index + 1;

    if (nextIndex < 0 || nextIndex >= timeline.entries.length) {
      return;
    }

    const nextRoute = timeline.entries[nextIndex];

    setNativeRouteTimelines((current) => ({
      ...current,
      [activeTab.id]: {
        entries: timeline.entries,
        index: nextIndex
      }
    }));

    handleTabChange(activeTab.id, {
      url: nextRoute,
      title: getUrlLabel(nextRoute),
      loading: true,
      canGoBack: nextIndex > 0,
      canGoForward: nextIndex < timeline.entries.length - 1,
      lastVisitedAt: Date.now()
    });
    setAddressDraft(nextRoute);
  };

  const navigateTab = (tabId: string, rawTarget: string) => {
    const normalizedTarget = normalizeBrowserTarget(rawTarget, settings.searchEngine);

    if (!normalizedTarget) {
      setBrowserNotice(
        'WaterFall accepts http, https, waterfall:// routes, or a search query.'
      );
      return;
    }

    setBrowserNotice('');
    if (
      normalizedTarget === WATERFALL_SITE_SHIELD_ROUTE &&
      tabId === activeTab.id &&
      activeTab.url &&
      normalizeWaterfallRoute(activeTab.url) !== WATERFALL_SITE_SHIELD_ROUTE
    ) {
      setSiteShieldTargetUrl(activeTab.url);
    }

    const nativeNavigationState = isWaterfallRoute(normalizedTarget)
      ? syncNativeRouteNavigationState(tabId, normalizedTarget, 'push')
      : {
          canGoBack: false,
          canGoForward: false
        };
    handleTabChange(tabId, {
      url: normalizedTarget,
      title: getUrlLabel(normalizedTarget),
      loading: true,
      canGoBack: nativeNavigationState.canGoBack,
      canGoForward: nativeNavigationState.canGoForward,
      lastVisitedAt: Date.now()
    });
    setActiveTabId(tabId);
    setAddressDraft(normalizedTarget);
  };

  const handleAddressSubmit = () => {
    navigateTab(activeTab.id, addressDraft || settings.homePage);
  };

  const handleCreateTab = (targetUrl = '') => {
    const nextTab = createBlankTab();

    if (targetUrl) {
      const normalizedTarget = normalizeBrowserTarget(targetUrl, settings.searchEngine);
      if (normalizedTarget) {
        if (
          normalizedTarget === WATERFALL_SITE_SHIELD_ROUTE &&
          activeTab.url &&
          normalizeWaterfallRoute(activeTab.url) !== WATERFALL_SITE_SHIELD_ROUTE
        ) {
          setSiteShieldTargetUrl(activeTab.url);
        }
        nextTab.url = normalizedTarget;
        nextTab.title = getUrlLabel(normalizedTarget);
        nextTab.loading = true;
        if (isWaterfallRoute(normalizedTarget)) {
          nextTab.canGoBack = false;
          nextTab.canGoForward = false;
          setNativeRouteTimelines((current) => ({
            ...current,
            [nextTab.id]: {
              entries: [normalizeWaterfallRoute(normalizedTarget)],
              index: 0
            }
          }));
        }
      }
    }

    setTabs((current) => [...current, nextTab]);
    setActiveTabId(nextTab.id);
    setBrowserNotice('');
  };

  const handleCloseTab = (tabId: string) => {
    setTabs((current) => {
      if (current.length === 1) {
        const freshTab = createBlankTab();
        setActiveTabId(freshTab.id);
        setNativeRouteTimelines({});
        return [freshTab];
      }

      const currentIndex = current.findIndex((tab) => tab.id === tabId);
      const remainingTabs = current.filter((tab) => tab.id !== tabId);

      if (tabId === activeTabId) {
        const fallbackTab =
          remainingTabs[Math.max(0, currentIndex - 1)] || remainingTabs[0];
        setActiveTabId(fallbackTab.id);
      }

      return remainingTabs;
    });
    setNativeRouteTimelines((current) => {
      const nextTimelines = { ...current };
      delete nextTimelines[tabId];
      return nextTimelines;
    });
  };

  const toggleBookmarkForTarget = (targetUrl: string, title?: string) => {
    if (!targetUrl) {
      return;
    }

    setBookmarks((current) => {
      const existing = current.find((bookmark) => bookmark.url === targetUrl);

      if (existing) {
        return current.filter((bookmark) => bookmark.id !== existing.id);
      }

      return [
        {
          id: createId('bookmark'),
          title: title || getUrlLabel(targetUrl),
          url: targetUrl,
          createdAt: Date.now()
        },
        ...current
      ].slice(0, 12);
    });
  };

  const handleToggleBookmark = () => {
    if (!activeTab.url) {
      return;
    }

    toggleBookmarkForTarget(activeTab.url, activeTab.title || getUrlLabel(activeTab.url));
  };

  const handleClearHistory = () => {
    setHistory([]);
    setBrowserNotice('WaterFall cleared the native history deck.');
  };

  const handleNativeSettingToggle = (
    settingPath: WaterfallNativeSettingPath,
    settingValue?: boolean
  ) => {
    setSettings((current) => {
      switch (settingPath) {
        case 'restoreSession':
          return {
            ...current,
            restoreSession: settingValue ?? !current.restoreSession
          };
        case 'privacy.doNotTrack':
          return {
            ...current,
            privacy: {
              ...current.privacy,
              doNotTrack: settingValue ?? !current.privacy.doNotTrack
            }
          };
        case 'privacy.globalPrivacyControl':
          return {
            ...current,
            privacy: {
              ...current.privacy,
              globalPrivacyControl:
                settingValue ?? !current.privacy.globalPrivacyControl
            }
          };
        case 'privacy.blockTrackers':
          return {
            ...current,
            privacy: {
              ...current.privacy,
              blockTrackers: settingValue ?? !current.privacy.blockTrackers
            }
          };
        case 'privacy.httpsOnlyMode':
          return {
            ...current,
            privacy: {
              ...current.privacy,
              httpsOnlyMode: settingValue ?? !current.privacy.httpsOnlyMode
            }
          };
        case 'privacy.masterKillSwitch':
          return {
            ...current,
            privacy: {
              ...current.privacy,
              masterKillSwitch: settingValue ?? !current.privacy.masterKillSwitch
            }
          };
        case 'privacy.permissionsLockdown':
          return {
            ...current,
            privacy: {
              ...current.privacy,
              permissionsLockdown:
                settingValue ?? !current.privacy.permissionsLockdown
            }
          };
        case 'privacy.stripReferrers':
          return {
            ...current,
            privacy: {
              ...current.privacy,
              stripReferrers: settingValue ?? !current.privacy.stripReferrers
            }
          };
        case 'privacy.antiFingerprinting':
          return {
            ...current,
            privacy: {
              ...current.privacy,
              antiFingerprinting:
                settingValue ?? !current.privacy.antiFingerprinting
            }
          };
        case 'privacy.blockPopups':
          return {
            ...current,
            privacy: {
              ...current.privacy,
              blockPopups: settingValue ?? !current.privacy.blockPopups
            }
          };
        case 'security.scanDownloadsOnStart':
          return {
            ...current,
            security: {
              ...current.security,
              scanDownloadsOnStart:
                settingValue ?? !current.security.scanDownloadsOnStart
            }
          };
        case 'security.scanDownloadsOnCompletion':
          return {
            ...current,
            security: {
              ...current.security,
              scanDownloadsOnCompletion:
                settingValue ?? !current.security.scanDownloadsOnCompletion
            }
          };
        case 'security.quarantineHighRiskDownloads':
          return {
            ...current,
            security: {
              ...current.security,
              quarantineHighRiskDownloads:
                settingValue ?? !current.security.quarantineHighRiskDownloads
            }
          };
        case 'security.strictScopeMode':
          return {
            ...current,
            security: {
              ...current.security,
              strictScopeMode:
                settingValue ?? !current.security.strictScopeMode
            }
          };
        case 'security.nativeArtifactScanning':
          return {
            ...current,
            security: {
              ...current.security,
              nativeArtifactScanning:
                settingValue ?? !current.security.nativeArtifactScanning
            }
          };
        case 'security.externalAuthorizedScanning':
          return {
            ...current,
            security: {
              ...current.security,
              externalAuthorizedScanning:
                settingValue ?? !current.security.externalAuthorizedScanning
            }
          };
        case 'security.exportEvidenceBundles':
          return {
            ...current,
            security: {
              ...current.security,
              exportEvidenceBundles:
                settingValue ?? !current.security.exportEvidenceBundles
            }
          };
        case 'collective.enabled':
          return {
            ...current,
            collective: {
              ...current.collective,
              enabled: settingValue ?? !current.collective.enabled
            }
          };
        case 'collective.cpuEnabled':
          return {
            ...current,
            collective: {
              ...current.collective,
              cpuEnabled: settingValue ?? !current.collective.cpuEnabled
            }
          };
        case 'collective.gpuEnabled':
          return {
            ...current,
            collective: {
              ...current.collective,
              gpuEnabled: settingValue ?? !current.collective.gpuEnabled
            }
          };
        default:
          return current;
      }
    });
  };

  const handleNativeSettingValue = (
    settingPath: WaterfallNativeSettingPath,
    stringValue?: string,
    numberValue?: number
  ) => {
    if (settingPath === 'homePage') {
      const normalizedTarget = normalizeHomePageTarget(stringValue || '', settings.searchEngine);

      if (!normalizedTarget) {
        setBrowserNotice(
          'WaterFall home pages must be a direct waterfall://, http://, or https:// target.'
        );
        setSettingsHomeDraft(settings.homePage);
        return;
      }

      setSettings((current) => ({
        ...current,
        homePage: normalizedTarget
      }));
      setSettingsHomeDraft(normalizedTarget);
      setBrowserNotice('');
      return;
    }

    if (settingPath === 'searchEngine') {
      const nextSearchEngine = SEARCH_ENGINE_VALUES.includes(stringValue as WaterfallSearchEngine)
        ? (stringValue as WaterfallSearchEngine)
        : null;

      if (!nextSearchEngine) {
        setBrowserNotice('WaterFall rejected an unknown native search engine value.');
        return;
      }

      setSettings((current) => ({
        ...current,
        searchEngine: nextSearchEngine
      }));
      setBrowserNotice('');
      return;
    }

    setSettings((current) => {
      switch (settingPath) {
        case 'collective.cpuLimitPercent':
          return {
            ...current,
            collective: {
              ...current.collective,
              cpuLimitPercent: Math.min(
                90,
                Math.max(5, numberValue ?? current.collective.cpuLimitPercent)
              )
            }
          };
        case 'collective.gpuLimitPercent':
          return {
            ...current,
            collective: {
              ...current.collective,
              gpuLimitPercent: Math.min(
                90,
                Math.max(5, numberValue ?? current.collective.gpuLimitPercent)
              )
            }
          };
        case 'collective.sessionCapMinutes':
          return {
            ...current,
            collective: {
              ...current.collective,
              sessionCapMinutes: Math.min(
                240,
                Math.max(5, numberValue ?? current.collective.sessionCapMinutes)
              )
            }
          };
        default:
          return current;
      }
    });
    setBrowserNotice('');
  };

  const handleResetSession = () => {
    const freshSession = createDefaultSession();
    setTabs(freshSession.tabs);
    setNativeRouteTimelines(seedNativeRouteTimelines(freshSession.tabs));
    setActiveTabId(freshSession.activeTabId);
    setHistory([]);
    setBrowserNotice('WaterFall reset the live session and reopened the launch pad.');
  };

  const handleOpenExternal = async () => {
    if (!window.electron?.browser || !activeTab.url || activeTabIsInternalRoute) {
      return;
    }

    try {
      await window.electron.browser.openExternal(activeTab.url);
    } catch (error) {
      setBrowserNotice(
        error instanceof Error
          ? error.message
          : 'WaterFall could not hand this route to the system browser.'
      );
    }
  };

  const handleShowDownload = async (filePath: string) => {
    if (!window.electron?.browser) {
      return;
    }

    try {
      await window.electron.browser.showDownloadItem(filePath);
    } catch (error) {
      setBrowserNotice(
        error instanceof Error ? error.message : 'WaterFall could not reveal the download.'
      );
    }
  };

  const handleAddExtension = async () => {
    if (!window.electron?.browser) {
      return;
    }

    try {
      const nextExtensions = await window.electron.browser.addExtension();
      setExtensions(nextExtensions);
      setBrowserNotice('WaterFall refreshed its extension deck.');
    } catch (error) {
      setBrowserNotice(
        error instanceof Error ? error.message : 'WaterFall could not add that extension.'
      );
    }
  };

  const handleRemoveExtension = async (extensionPath: string) => {
    if (!window.electron?.browser) {
      return;
    }

    try {
      const nextExtensions = await window.electron.browser.removeExtension(extensionPath);
      setExtensions(nextExtensions);
      setBrowserNotice('WaterFall refreshed its extension deck.');
    } catch (error) {
      setBrowserNotice(
        error instanceof Error ? error.message : 'WaterFall could not remove that extension.'
      );
    }
  };

  const handleApplyUpdate = async () => {
    if (!window.waterfall?.updates || !updateManifest) {
      return;
    }

    setUpdatesLoading(true);
    setUpdateError('');

    try {
      const stagedManifest = await window.waterfall.updates.apply(updateManifest);
      setUpdateManifest(stagedManifest);
      setBrowserNotice(
        stagedManifest.statusMessage ||
          `WaterFall staged update ${stagedManifest.version} for the next verified rollout step.`
      );
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'WaterFall could not stage that verified update.';
      setUpdateError(message);
      setBrowserNotice(message);
    } finally {
      setUpdatesLoading(false);
    }
  };

  const handleScanDownloadRecord = async (downloadId: string) => {
    if (!window.electron?.browser) {
      return;
    }

    try {
      const nextRecord = await window.electron.browser.scanDownloadRecord(downloadId);
      if (!nextRecord) {
        return;
      }

      setDownloads((current) =>
        current
          .map((download) => (download.id === nextRecord.id ? nextRecord : download))
          .sort((left, right) => right.startedAt - left.startedAt)
      );
      setBrowserNotice(
        `WaterFall rescanned ${nextRecord.filename} with verdict ${nextRecord.securityScan?.verdict || 'unknown'}.`
      );
      void refreshSecurityStatus(true);
    } catch (error) {
      setBrowserNotice(
        error instanceof Error ? error.message : 'WaterFall could not rescan that download.'
      );
    }
  };

  const handleReleaseDownloadQuarantine = async (downloadId: string) => {
    if (!window.electron?.browser) {
      return;
    }

    try {
      const nextRecord = await window.electron.browser.releaseDownloadQuarantine(downloadId);
      if (!nextRecord) {
        return;
      }

      setDownloads((current) =>
        current
          .map((download) => (download.id === nextRecord.id ? nextRecord : download))
          .sort((left, right) => right.startedAt - left.startedAt)
      );
      setBrowserNotice(`WaterFall released ${nextRecord.filename} from quarantine.`);
      void refreshSecurityStatus(true);
    } catch (error) {
      setBrowserNotice(
        error instanceof Error
          ? error.message
          : 'WaterFall could not release that quarantined artifact.'
      );
    }
  };

  const handleExportSecurityReport = async () => {
    if (!window.electron?.browser) {
      return;
    }

    try {
      const reportPath = await window.electron.browser.exportSecurityReport();
      if (reportPath) {
        setBrowserNotice(`WaterFall exported a security report to ${reportPath}.`);
      }
    } catch (error) {
      setBrowserNotice(
        error instanceof Error ? error.message : 'WaterFall could not export that security report.'
      );
    }
  };

  const handleExportBountyPack = async () => {
    if (!window.electron?.browser) {
      return;
    }

    try {
      const bundlePath = await window.electron.browser.exportBountyPack();
      if (bundlePath) {
        setBrowserNotice(`WaterFall exported a bounty pack to ${bundlePath}.`);
      }
    } catch (error) {
      setBrowserNotice(
        error instanceof Error ? error.message : 'WaterFall could not export that bounty pack.'
      );
    }
  };

  const handleSetVpnState = async (enabled: boolean) => {
    if (!window.waterfall?.security) {
      return;
    }

    try {
      const vpnTargetUrl =
        normalizeWaterfallRoute(activeTab.url) === WATERFALL_SITE_SHIELD_ROUTE && siteShieldTargetUrl
          ? siteShieldTargetUrl
          : activeTab.url;
      let vpnServer = 'waterfall-secure';

      if (vpnTargetUrl && !isWaterfallRoute(vpnTargetUrl)) {
        try {
          vpnServer = new URL(vpnTargetUrl).hostname || vpnServer;
        } catch {
          vpnServer = 'waterfall-secure';
        }
      }

      await window.waterfall.security.setVPNState({
        enabled,
        server: enabled ? vpnServer : ''
      });
      await Promise.all([refreshSecurityStatus(true), refreshBridgeHealth(true)]);
      setBrowserNotice(
        enabled
          ? 'WaterFall asked the orchestrator bridge to enable the built-in VPN lane.'
          : 'WaterFall asked the orchestrator bridge to disable the built-in VPN lane.'
      );
    } catch (error) {
      setBrowserNotice(
        error instanceof Error
          ? error.message
          : 'WaterFall could not update the VPN state through the orchestrator bridge.'
      );
    }
  };

  const handleExportProfile = async () => {
    if (!window.waterfall?.profile) {
      return;
    }

    const profileBundle: WaterfallProfileBundle = {
      version: 1,
      exportedAt: Date.now(),
      settings,
      session: {
        tabs,
        activeTabId,
        bookmarks,
        history
      }
    };

    try {
      const exportPassphrase = window.prompt(
        'Enter a passphrase to encrypt this WaterFall backup.',
        ''
      );
      if (exportPassphrase === null) {
        return;
      }

      const exportPassphraseConfirmation = window.prompt(
        'Re-enter the WaterFall backup passphrase.',
        ''
      );
      if (exportPassphraseConfirmation === null) {
        return;
      }

      if (!exportPassphrase || exportPassphrase !== exportPassphraseConfirmation) {
        setBrowserNotice('WaterFall backup export requires matching passphrases.');
        return;
      }

      const exportPath = await window.waterfall.profile.exportBundle(profileBundle, exportPassphrase);
      if (exportPath) {
        setBrowserNotice(`WaterFall exported an encrypted backup to ${exportPath}.`);
      }
    } catch (error) {
      setBrowserNotice(
        error instanceof Error ? error.message : 'WaterFall could not export that encrypted backup.'
      );
    }
  };

  const handleImportProfile = async () => {
    if (!window.waterfall?.profile) {
      return;
    }

    try {
      const importPassphrase = window.prompt(
        'Enter the passphrase for the WaterFall backup you want to import.',
        ''
      );
      if (importPassphrase === null) {
        return;
      }

      const importedProfile = await window.waterfall.profile.importBundle(importPassphrase);

      if (!importedProfile) {
        return;
      }

      const nextSettings = sanitizeSettings(importedProfile.settings);
      const nextSession = sanitizeSession(importedProfile.session);

      setSettings(nextSettings);
      setTabs(nextSession.tabs);
      setActiveTabId(nextSession.activeTabId);
      setBookmarks(nextSession.bookmarks);
      setHistory(nextSession.history);
      setBrowserNotice('WaterFall imported the backup and restored its deck.');
    } catch (error) {
      setBrowserNotice(
        error instanceof Error ? error.message : 'WaterFall could not import that backup.'
      );
    }
  };

  const handleCopyMeshIdentity = async () => {
    try {
      await navigator.clipboard.writeText(settings.account.nodeId);
      setBrowserNotice('WaterFall copied the mesh node identity to the clipboard.');
    } catch {
      setBrowserNotice(`Mesh node identity: ${settings.account.nodeId}`);
    }
  };

  const handleNativeRouteRendered = useCallback((
    tabId: string,
    renderResult: WaterfallNativeRenderResult
  ) => {
    const nativeNavigationState = syncNativeRouteNavigationState(tabId, renderResult.route, 'replace');
    setBrowserNotice('');
    handleTabChange(tabId, {
      title: renderResult.title,
      url: renderResult.route,
      loading: false,
      canGoBack: nativeNavigationState.canGoBack,
      canGoForward: nativeNavigationState.canGoForward,
      lastVisitedAt: Date.now()
    });
    handleHistoryEntry({
      id: createId('history'),
      title: renderResult.title,
      url: renderResult.route,
      visitedAt: Date.now()
    });
  }, [handleHistoryEntry, handleTabChange]);

  const handleNativeRouteError = useCallback((tabId: string, message: string) => {
    const timeline = getNativeRouteTimeline(tabId);
    handleTabChange(tabId, {
      loading: false,
      canGoBack: timeline.index > 0,
      canGoForward: timeline.index >= 0 && timeline.index < timeline.entries.length - 1,
      lastVisitedAt: Date.now()
    });
    setBrowserNotice(message);
  }, [handleTabChange, nativeRouteTimelines]);

  const handleGoBackActiveTab = () => {
    if (activeTabIsInternalRoute) {
      navigateNativeHistory('back');
      return;
    }

    activeWebview?.goBack();
  };

  const handleGoForwardActiveTab = () => {
    if (activeTabIsInternalRoute) {
      navigateNativeHistory('forward');
      return;
    }

    activeWebview?.goForward();
  };

  const handleReloadActiveTab = () => {
    if (!activeTab.url) {
      return;
    }

    if (activeTabIsInternalRoute) {
      if (normalizeWaterfallRoute(activeTab.url) === WATERFALL_SECURITY_WORKBENCH_ROUTE) {
        void refreshSecurityStatus(true);
      }
      if (normalizeWaterfallRoute(activeTab.url) === WATERFALL_SITE_SHIELD_ROUTE) {
        void refreshSecurityStatus(true);
      }
      if (normalizeWaterfallRoute(activeTab.url) === WATERFALL_PRIVACY_AUDITOR_ROUTE) {
        void Promise.all([refreshSecurityStatus(true), refreshBridgeHealth(true)]);
      }
      if (normalizeWaterfallRoute(activeTab.url) === WATERFALL_SECURITY_ARCHITECT_ROUTE) {
        void Promise.all([refreshSecurityToolkitInventory(true), refreshSecurityStatus(true)]);
      }

      handleTabChange(activeTab.id, {
        loading: true,
        lastVisitedAt: Date.now()
      });
      setNativeReloadTokens((current) => ({
        ...current,
        [activeTab.id]: (current[activeTab.id] || 0) + 1
      }));
      return;
    }

    activeWebview?.reload();
  };

  const handleStopActiveTab = () => {
    if (activeTabIsInternalRoute) {
      handleTabChange(activeTab.id, {
        loading: false
      });
      return;
    }

    activeWebview?.stop();
  };

  const handleNativeRouteAction = (action: WaterfallNativeRouteAction) => {
    if (action.kind === 'navigate' && action.target) {
      navigateTab(activeTab.id, action.target);
      return;
    }

    if (action.kind === 'navigate-back') {
      handleGoBackActiveTab();
      return;
    }

    if (action.kind === 'navigate-forward') {
      handleGoForwardActiveTab();
      return;
    }

    if (action.kind === 'open-settings') {
      setSettingsOpen(true);
      return;
    }

    if (action.kind === 'show-download' && action.filePath) {
      void handleShowDownload(action.filePath);
      return;
    }

    if (action.kind === 'scan-download' && action.downloadId) {
      void handleScanDownloadRecord(action.downloadId);
      return;
    }

    if (action.kind === 'release-download-quarantine' && action.downloadId) {
      void handleReleaseDownloadQuarantine(action.downloadId);
      return;
    }

    if (action.kind === 'add-extension') {
      void handleAddExtension();
      return;
    }

    if (action.kind === 'remove-extension' && action.extensionPath) {
      void handleRemoveExtension(action.extensionPath);
      return;
    }

    if (action.kind === 'copy-node-id') {
      void handleCopyMeshIdentity();
      return;
    }

    if (action.kind === 'toggle-setting' && action.settingPath) {
      handleNativeSettingToggle(action.settingPath, action.settingValue);
      return;
    }

    if (action.kind === 'set-setting' && action.settingPath) {
      handleNativeSettingValue(action.settingPath, action.stringValue, action.numberValue);
      return;
    }

    if (action.kind === 'toggle-bookmark' && action.target) {
      toggleBookmarkForTarget(action.target, getUrlLabel(action.target));
      return;
    }

    if (action.kind === 'create-tab') {
      handleCreateTab(action.target || '');
      return;
    }

    if (action.kind === 'clear-history') {
      handleClearHistory();
      return;
    }

    if (action.kind === 'reset-session') {
      handleResetSession();
      return;
    }

    if (action.kind === 'export-security-report') {
      void handleExportSecurityReport();
      return;
    }

    if (action.kind === 'export-bounty-pack') {
      void handleExportBountyPack();
      return;
    }

    if (action.kind === 'enable-vpn') {
      void handleSetVpnState(true);
      return;
    }

    if (action.kind === 'disable-vpn') {
      void handleSetVpnState(false);
      return;
    }

    if (action.kind === 'check-updates') {
      void refreshUpdateManifest();
      return;
    }

    if (action.kind === 'apply-update') {
      void handleApplyUpdate();
      return;
    }

    if (action.kind === 'refresh') {
      handleReloadActiveTab();
    }
  };

  return (
    <Box
      sx={{
        height: '100%',
        minHeight: 0,
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <Stack direction="row" spacing={1} alignItems="center" useFlexGap flexWrap="wrap">
        <Chip
          label="Thirsty's WaterFall"
          size="small"
          sx={{ color: '#f5e6a6', border: '1px solid #7d6b2d', bgcolor: '#353015' }}
        />
        <Chip
          label="Multi-tab shell"
          size="small"
          sx={{ color: '#cde9e1', border: '1px solid #35624f', bgcolor: '#18261f' }}
        />
        <Chip
          label={activeTab.loading ? 'Flowing' : 'Ready'}
          size="small"
          sx={{ color: activeTab.loading ? '#7dd3fc' : '#86efac' }}
        />
        <Chip
          label={settings.privacy.masterKillSwitch ? 'Kill Switch Armed' : 'Kill Switch Idle'}
          size="small"
          sx={{ color: settings.privacy.masterKillSwitch ? '#fca5a5' : '#94a3b8' }}
        />
        <Chip
          label={
            settings.collective.enabled
              ? `Collective pledge: ${collectiveProjection.localUnits} units`
              : 'Collective pledge offline'
          }
          size="small"
          sx={{ color: settings.collective.enabled ? '#fbbf24' : '#94a3b8' }}
        />
      </Stack>

      <Box
        sx={{
          mt: 1.25,
          display: 'flex',
          gap: 1,
          overflowX: 'auto',
          pb: 0.5
        }}
      >
        {tabs.map((tab) => (
          <Box
            key={tab.id}
            onClick={() => {
              setActiveTabId(tab.id);
              setBrowserNotice('');
            }}
            sx={{
              minWidth: 208,
              display: 'flex',
              alignItems: 'center',
              gap: 0.75,
              px: 1,
              py: 0.75,
              border: '2px solid rgba(96, 117, 87, 0.9)',
              bgcolor: tab.id === activeTabId ? '#263023' : '#1b2017',
              color: tab.id === activeTabId ? '#f5e6a6' : '#d7e3c5',
              cursor: 'pointer',
              boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
            }}
          >
            <TravelExplore sx={{ fontSize: 16, color: tab.loading ? '#7dd3fc' : '#fbbf24' }} />
            <Typography variant="body2" sx={{ flex: 1, minWidth: 0 }} noWrap>
              {tab.title || getUrlLabel(tab.url)}
            </Typography>
            <IconButton
              size="small"
              onClick={(event) => {
                event.stopPropagation();
                handleCloseTab(tab.id);
              }}
              sx={{ color: 'inherit', borderRadius: 0 }}
            >
              <Close fontSize="small" />
            </IconButton>
          </Box>
        ))}

        <Button
          onClick={() => handleCreateTab()}
          startIcon={<Add />}
          sx={{
            minWidth: 144,
            color: '#f3f7df',
            border: '2px solid rgba(96, 117, 87, 0.9)',
            bgcolor: '#1f261c',
            boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
          }}
        >
          New Tab
        </Button>
      </Box>

      <Stack
        direction={{ xs: 'column', lg: 'row' }}
        spacing={1}
        alignItems={{ xs: 'stretch', lg: 'center' }}
        sx={{ mt: 1 }}
      >
        <Stack direction="row" spacing={0.5}>
            <IconButton
              size="small"
              disabled={!activeTab.canGoBack}
              onClick={handleGoBackActiveTab}
              sx={{ color: '#f3f7df', borderRadius: 0 }}
            >
              <ArrowBack fontSize="small" />
            </IconButton>
            <IconButton
              size="small"
              disabled={!activeTab.canGoForward}
              onClick={handleGoForwardActiveTab}
              sx={{ color: '#f3f7df', borderRadius: 0 }}
            >
            <ArrowForward fontSize="small" />
          </IconButton>
          <IconButton
            size="small"
            onClick={handleReloadActiveTab}
            disabled={!activeTab.url}
            sx={{ color: '#f3f7df', borderRadius: 0 }}
          >
            <Refresh fontSize="small" />
          </IconButton>
          <IconButton
            size="small"
            onClick={handleStopActiveTab}
            disabled={!activeTab.loading || activeTabIsInternalRoute}
            sx={{ color: '#f3f7df', borderRadius: 0 }}
          >
            <Stop fontSize="small" />
          </IconButton>
          <IconButton
            size="small"
            onClick={() => navigateTab(activeTab.id, settings.homePage)}
            sx={{ color: '#f3f7df', borderRadius: 0 }}
          >
            <Home fontSize="small" />
          </IconButton>
        </Stack>

        <TextField
          inputRef={addressInputRef}
          value={addressDraft}
          onChange={(event) => setAddressDraft(event.target.value)}
          onFocus={() => setAddressFocused(true)}
          onBlur={() => setAddressFocused(false)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              event.preventDefault();
              handleAddressSubmit();
            }
          }}
          placeholder="Enter a route, waterfall:// page, or search the web"
          fullWidth
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search sx={{ fontSize: 18, color: '#7dd3fc' }} />
              </InputAdornment>
            )
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              bgcolor: '#1f261c',
              color: '#f3f7df',
              fontFamily: 'var(--font-code)',
              borderRadius: 0,
              '& fieldset': {
                borderWidth: 2,
                borderColor: 'rgba(96, 117, 87, 0.9)'
              }
            }
          }}
        />

        <Stack direction="row" spacing={0.5}>
          <IconButton
            size="small"
            onClick={handleToggleBookmark}
            disabled={!activeTab.url}
            sx={{ color: bookmarked ? '#f4ba3f' : '#f3f7df', borderRadius: 0 }}
          >
            <BookmarkAdd fontSize="small" />
          </IconButton>
          <IconButton
            size="small"
            onClick={() => setSettingsOpen(true)}
            sx={{ color: '#f3f7df', borderRadius: 0 }}
          >
            <Settings fontSize="small" />
          </IconButton>
          <IconButton
            size="small"
            onClick={() => {
              void handleOpenExternal();
            }}
            disabled={!activeTab.url || activeTabIsInternalRoute}
            sx={{ color: '#f3f7df', borderRadius: 0 }}
          >
            <Launch fontSize="small" />
          </IconButton>
          <Button
            onClick={handleAddressSubmit}
            variant="contained"
            sx={{
              minWidth: 112,
              background: 'linear-gradient(135deg, #f4ba3f 0%, #59b1a6 100%)',
              color: '#10150f',
              boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
            }}
          >
            Go
          </Button>
        </Stack>
      </Stack>

      {bookmarks.length > 0 && (
        <Stack direction="row" spacing={0.75} useFlexGap flexWrap="wrap" sx={{ mt: 1.2 }}>
          {bookmarks.slice(0, 8).map((bookmark) => (
            <Button
              key={bookmark.id}
              size="small"
              onClick={() => navigateTab(activeTab.id, bookmark.url)}
              sx={{
                color: '#d7e3c5',
                border: '1px solid rgba(96, 117, 87, 0.9)',
                bgcolor: '#1f261c',
                borderRadius: 0,
                fontFamily: 'var(--font-code)',
                fontSize: 11
              }}
            >
              {bookmark.title}
            </Button>
          ))}
        </Stack>
      )}

      {browserNotice && (
        <Alert
          severity="info"
          sx={{
            mt: 1.5,
            bgcolor: '#221b12',
            border: '2px solid rgba(96, 117, 87, 0.9)',
            borderRadius: 0
          }}
        >
          {browserNotice}
        </Alert>
      )}

      <Box
        sx={{
          flex: 1,
          minHeight: 0,
          mt: 1.5,
          border: '2px solid rgba(96, 117, 87, 0.9)',
          bgcolor: '#090c08',
          overflow: 'hidden',
          position: 'relative',
          boxShadow: 'inset 0 0 0 2px rgba(10, 13, 9, 0.9)'
        }}
      >
        {tabs.map((tab) => (
          <WaterfallTabPane
            key={tab.id}
            tab={tab}
            active={tab.id === activeTabId}
            onNodeChange={handleNodeChange}
            onTabChange={handleTabChange}
            onHistoryEntry={handleHistoryEntry}
          />
        ))}

        {tabs.map((tab) => (
          <WaterfallNativeRoutePane
            key={`native-${tab.id}`}
            tab={tab}
            active={tab.id === activeTabId && isWaterfallRoute(tab.url)}
            reloadToken={nativeReloadTokens[tab.id] || 0}
            nativeDocument={nativeDocumentsByRoute[normalizeWaterfallRoute(tab.url)] || null}
            actions={nativeRouteActionsByRoute[normalizeWaterfallRoute(tab.url)] || []}
            onAction={handleNativeRouteAction}
            onRendered={handleNativeRouteRendered}
            onRenderError={handleNativeRouteError}
          />
        ))}

        {!activeTab.url && (
          <Box
            sx={{
              height: '100%',
              p: 3,
              display: 'grid',
              gap: 2,
              gridTemplateColumns: {
                xs: '1fr',
                xl: 'minmax(0, 1.35fr) minmax(320px, 0.65fr)'
              },
              overflow: 'auto'
            }}
          >
            <Box>
              <Typography
                variant="overline"
                sx={{ color: '#f4ba3f', letterSpacing: 2.1, fontWeight: 700 }}
              >
                WaterFall Launch Pad
              </Typography>
              <Typography
                variant="h4"
                sx={{
                  mt: 0.5,
                  fontWeight: 800,
                  color: '#f5e6a6',
                  fontFamily: 'var(--font-code)'
                }}
              >
                Thirsty&apos;s WaterFall
              </Typography>
              <Typography variant="body1" sx={{ mt: 1.2, color: '#c7d0b1', maxWidth: 760 }}>
                A sovereign browser shell inside the workstation: tabs, routes, bookmarks,
                session memory, and local-first settings under your control. This is WaterFall&apos;s
                own deck, not a copy of another browser&apos;s chrome.
              </Typography>

              <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mt: 1.75 }}>
                <Chip label="Tabs" sx={{ color: '#7dd3fc' }} />
                <Chip label="Bookmarks" sx={{ color: '#fbbf24' }} />
                <Chip label="History" sx={{ color: '#c4b5fd' }} />
                <Chip label="Settings" sx={{ color: '#86efac' }} />
                <Chip label="Local Controls" sx={{ color: '#fca5a5' }} />
              </Stack>

              <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mt: 2 }}>
                <Button
                  onClick={() => navigateTab(activeTab.id, 'waterfall://home')}
                  variant="contained"
                  startIcon={<AutoAwesome />}
                  sx={{
                    background: 'linear-gradient(135deg, #59b1a6 0%, #7dd3fc 100%)',
                    color: '#09110f',
                    boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                  }}
                >
                  Native Home
                </Button>
                <Button
                  onClick={() => navigateTab(activeTab.id, 'waterfall://engine-lab')}
                  startIcon={<Bolt />}
                  sx={{
                    color: '#f3f7df',
                    border: '2px solid rgba(96, 117, 87, 0.9)',
                    bgcolor: '#12201d',
                    boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                  }}
                >
                  Engine Lab
                </Button>
                <Button
                  onClick={() => navigateTab(activeTab.id, 'waterfall://history')}
                  startIcon={<AutoAwesome />}
                  sx={{
                    color: '#f3f7df',
                    border: '2px solid rgba(96, 117, 87, 0.9)',
                    bgcolor: '#1b2430',
                    boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                  }}
                >
                  History Deck
                </Button>
                <Button
                  onClick={() => navigateTab(activeTab.id, 'waterfall://bookmarks')}
                  startIcon={<BookmarkAdd />}
                  sx={{
                    color: '#f3f7df',
                    border: '2px solid rgba(96, 117, 87, 0.9)',
                    bgcolor: '#2d2210',
                    boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                  }}
                >
                  Bookmark Deck
                </Button>
                <Button
                  onClick={() => navigateTab(activeTab.id, 'waterfall://downloads')}
                  startIcon={<Download />}
                  sx={{
                    color: '#f3f7df',
                    border: '2px solid rgba(96, 117, 87, 0.9)',
                    bgcolor: '#302414',
                    boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                  }}
                >
                  Download Deck
                </Button>
                <Button
                  onClick={() => navigateTab(activeTab.id, 'waterfall://settings')}
                  startIcon={<Settings />}
                  sx={{
                    color: '#f3f7df',
                    border: '2px solid rgba(96, 117, 87, 0.9)',
                    bgcolor: '#19281a',
                    boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                  }}
                >
                  Native Settings
                </Button>
                <Button
                  onClick={() => navigateTab(activeTab.id, WATERFALL_SECURITY_WORKBENCH_ROUTE)}
                  startIcon={<Shield />}
                  sx={{
                    color: '#f3f7df',
                    border: '2px solid rgba(96, 117, 87, 0.9)',
                    bgcolor: '#302414',
                    boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                  }}
                >
                  Security Workbench
                </Button>
                <Button
                  onClick={() => navigateTab(activeTab.id, WATERFALL_SITE_SHIELD_ROUTE)}
                  startIcon={<PrivacyTip />}
                  sx={{
                    color: '#f3f7df',
                    border: '2px solid rgba(96, 117, 87, 0.9)',
                    bgcolor: '#1f261c',
                    boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                  }}
                >
                  Site Shield
                </Button>
                <Button
                  onClick={() => navigateTab(activeTab.id, WATERFALL_PRIVACY_AUDITOR_ROUTE)}
                  startIcon={<PrivacyTip />}
                  sx={{
                    color: '#f3f7df',
                    border: '2px solid rgba(96, 117, 87, 0.9)',
                    bgcolor: '#19281a',
                    boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                  }}
                >
                  Privacy Auditor
                </Button>
                <Button
                  onClick={() => navigateTab(activeTab.id, WATERFALL_SECURITY_ARCHITECT_ROUTE)}
                  startIcon={<Shield />}
                  sx={{
                    color: '#f3f7df',
                    border: '2px solid rgba(96, 117, 87, 0.9)',
                    bgcolor: '#302414',
                    boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                  }}
                >
                  Security Architect
                </Button>
                <Button
                  onClick={() => navigateTab(activeTab.id, WATERFALL_UPDATES_ROUTE)}
                  startIcon={<Shield />}
                  sx={{
                    color: '#f3f7df',
                    border: '2px solid rgba(96, 117, 87, 0.9)',
                    bgcolor: '#302414',
                    boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                  }}
                >
                  Update Deck
                </Button>
                <Button
                  onClick={() => navigateTab(activeTab.id, settings.homePage)}
                  variant="contained"
                  startIcon={<Home />}
                  sx={{
                    background: 'linear-gradient(135deg, #f4ba3f 0%, #59b1a6 100%)',
                    color: '#10150f',
                    boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                  }}
                >
                  Open Home
                </Button>
                <Button
                  onClick={() => navigateTab(activeTab.id, WATERFALL_SEARCH_ROUTE)}
                  startIcon={<Search />}
                  sx={{
                    color: '#f3f7df',
                    border: '2px solid rgba(96, 117, 87, 0.9)',
                    bgcolor: '#1f261c',
                    boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                  }}
                >
                  Search Deck
                </Button>
                <Button
                  onClick={() => navigateTab(activeTab.id, 'http://localhost:8001')}
                  startIcon={<TravelExplore />}
                  sx={{
                    color: '#f3f7df',
                    border: '2px solid rgba(96, 117, 87, 0.9)',
                    bgcolor: '#1f261c',
                    boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                  }}
                >
                  Localhost
                </Button>
              </Stack>
            </Box>

            <Stack spacing={1.5}>
              <Box
                sx={{
                  p: 1.5,
                  border: '2px solid rgba(96, 117, 87, 0.9)',
                  bgcolor: 'rgba(29, 36, 27, 0.94)',
                  boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                }}
              >
                <Stack direction="row" spacing={1} alignItems="center">
                  <AutoAwesome fontSize="small" sx={{ color: '#f4ba3f' }} />
                  <Typography variant="subtitle2">Recent Routes</Typography>
                </Stack>
                <Stack spacing={0.9} sx={{ mt: 1.25 }}>
                  {history.length === 0 && (
                    <Typography variant="body2" sx={{ color: '#a5b39a' }}>
                      No routes recorded yet. Your first trip will appear here.
                    </Typography>
                  )}
                  {history.slice(0, 6).map((entry) => (
                    <Box
                      key={entry.id}
                      onClick={() => navigateTab(activeTab.id, entry.url)}
                      sx={{
                        p: 1,
                        cursor: 'pointer',
                        border: '1px solid rgba(96, 117, 87, 0.8)',
                        bgcolor: '#1f261c',
                        '&:hover': {
                          bgcolor: '#273025'
                        }
                      }}
                    >
                      <Typography variant="body2" noWrap>
                        {entry.title}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#94a3b8' }} noWrap>
                        {entry.url}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#6b7280', display: 'block' }}>
                        {formatVisitedAt(entry.visitedAt)}
                      </Typography>
                    </Box>
                  ))}
                </Stack>
              </Box>

              <Box
                sx={{
                  p: 1.5,
                  border: '2px solid rgba(96, 117, 87, 0.9)',
                  bgcolor: 'rgba(29, 36, 27, 0.94)',
                  boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                }}
              >
                <Stack direction="row" spacing={1} alignItems="center">
                  <Bolt fontSize="small" sx={{ color: '#7dd3fc' }} />
                  <Typography variant="subtitle2">Collective Readiness</Typography>
                </Stack>
                <Typography variant="body2" sx={{ mt: 1, color: '#c7d0b1' }}>
                  Settings include explicit CPU and GPU contribution controls, but nothing is
                  borrowed in the background unless the user opts in.
                </Typography>
                <Button
                  onClick={() => setSettingsOpen(true)}
                  size="small"
                  sx={{ mt: 1.25, color: '#f3f7df', borderRadius: 0 }}
                >
                  Open Settings
                </Button>
              </Box>

              <Box
                sx={{
                  p: 1.5,
                  border: '2px solid rgba(96, 117, 87, 0.9)',
                  bgcolor: 'rgba(29, 36, 27, 0.94)',
                  boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                }}
              >
                <Stack direction="row" spacing={1} alignItems="center">
                  <Download fontSize="small" sx={{ color: '#f4ba3f' }} />
                  <Typography variant="subtitle2">Download Hangar</Typography>
                </Stack>
                <Stack spacing={0.75} sx={{ mt: 1.25 }}>
                  {downloads.length === 0 && (
                    <Typography variant="body2" sx={{ color: '#a5b39a' }}>
                      Downloads will appear here as WaterFall captures them into your local
                      downloads folder.
                    </Typography>
                  )}
                  {downloads.slice(0, 3).map((download) => (
                    <Box
                      key={download.id}
                      onClick={() => {
                        void handleShowDownload(download.filePath);
                      }}
                      sx={{
                        p: 1,
                        cursor: 'pointer',
                        border: '1px solid rgba(96, 117, 87, 0.8)',
                        bgcolor: '#1f261c',
                        '&:hover': {
                          bgcolor: '#273025'
                        }
                      }}
                    >
                      <Typography variant="body2" noWrap>
                        {download.filename}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#94a3b8', display: 'block' }}>
                        {download.status} | {Math.round(download.receivedBytes / 1024)} KB
                      </Typography>
                    </Box>
                  ))}
                </Stack>
              </Box>

              <Box
                sx={{
                  p: 1.5,
                  border: '2px solid rgba(96, 117, 87, 0.9)',
                  bgcolor: 'rgba(29, 36, 27, 0.94)',
                  boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                }}
              >
                <Stack direction="row" spacing={1} alignItems="center">
                  <Extension fontSize="small" sx={{ color: '#7dd3fc' }} />
                  <Typography variant="subtitle2">Extension Deck</Typography>
                </Stack>
                <Typography variant="body2" sx={{ mt: 1, color: '#c7d0b1' }}>
                  Trusted unpacked extensions can be loaded into WaterFall’s own partition.
                </Typography>
                <Typography variant="caption" sx={{ mt: 0.75, display: 'block', color: '#a5b39a' }}>
                  {extensions.length} extension record(s) loaded.
                </Typography>
                <Button
                  onClick={() => {
                    void handleAddExtension();
                  }}
                  size="small"
                  sx={{ mt: 1.25, color: '#f3f7df', borderRadius: 0 }}
                >
                  Add Extension
                </Button>
              </Box>
            </Stack>
          </Box>
        )}
      </Box>

      <Drawer
        anchor="right"
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        PaperProps={{
          sx: {
            width: { xs: '100%', md: 420 },
            bgcolor: '#10150f',
            color: '#f3f7df',
            p: 2
          }
        }}
      >
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="overline" sx={{ color: '#f4ba3f', letterSpacing: 2 }}>
              Settings
            </Typography>
            <Typography
              variant="h5"
              sx={{ color: '#f5e6a6', fontWeight: 800, fontFamily: 'var(--font-code)' }}
            >
              WaterFall Control Deck
            </Typography>
          </Box>
          <IconButton onClick={() => setSettingsOpen(false)} sx={{ color: '#f3f7df', borderRadius: 0 }}>
            <Close />
          </IconButton>
        </Stack>

        <Alert
          severity="info"
          sx={{
            mt: 1.5,
            bgcolor: '#221b12',
            border: '2px solid rgba(96, 117, 87, 0.9)',
            borderRadius: 0
          }}
        >
          WaterFall is its own shell and interface, while Electron supplies the embedded runtime.
          The browser controls, tabs, memory, and settings here belong to WaterFall.
        </Alert>

        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" sx={{ color: '#f5e6a6' }}>
            Browser Identity
          </Typography>
          <TextField
            value={settingsHomeDraft}
            onChange={(event) => setSettingsHomeDraft(event.target.value)}
            onBlur={() => {
              const normalizedTarget = normalizeHomePageTarget(
                settingsHomeDraft,
                settings.searchEngine
              );

              if (!normalizedTarget) {
                setBrowserNotice(
                  'WaterFall home pages must be a direct waterfall://, http://, or https:// target.'
                );
                setSettingsHomeDraft(settings.homePage);
                return;
              }

              setSettings((current) => ({
                ...current,
                homePage: normalizedTarget
              }));
              setSettingsHomeDraft(normalizedTarget);
              setBrowserNotice('');
            }}
            label="Home page"
            fullWidth
            size="small"
            sx={{
              mt: 1.25,
              '& .MuiOutlinedInput-root': {
                bgcolor: '#1f261c',
                color: '#f3f7df',
                borderRadius: 0
              }
            }}
          />
          <TextField
            select
            label="Search engine"
            value={settings.searchEngine}
            onChange={(event) =>
              setSettings((current) => ({
                ...current,
                searchEngine: event.target.value as WaterfallSearchEngine
              }))
            }
            fullWidth
            size="small"
            sx={{
              mt: 1.25,
              '& .MuiOutlinedInput-root': {
                bgcolor: '#1f261c',
                color: '#f3f7df',
                borderRadius: 0
              }
            }}
          >
            {Object.entries(SEARCH_ENGINE_LABELS).map(([value, label]) => (
              <MenuItem key={value} value={value}>
                {label}
              </MenuItem>
            ))}
          </TextField>
          <FormControlLabel
            sx={{ mt: 1.25 }}
            control={
              <Switch
                checked={settings.restoreSession}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    restoreSession: event.target.checked
                  }))
                }
              />
            }
            label="Restore open tabs on next launch"
          />
        </Box>

        <Divider sx={{ my: 2, borderColor: 'rgba(96, 117, 87, 0.75)' }} />

        <Box>
          <Stack direction="row" spacing={1} alignItems="center">
            <AccountCircle fontSize="small" sx={{ color: '#f4ba3f' }} />
            <Typography variant="subtitle2" sx={{ color: '#f5e6a6' }}>
              Account And Mesh Identity
            </Typography>
          </Stack>
          <TextField
            label="Display name"
            value={settings.account.displayName}
            onChange={(event) =>
              setSettings((current) => ({
                ...current,
                account: {
                  ...current.account,
                  displayName: event.target.value
                }
              }))
            }
            fullWidth
            size="small"
            sx={{
              mt: 1.25,
              '& .MuiOutlinedInput-root': {
                bgcolor: '#1f261c',
                color: '#f3f7df',
                borderRadius: 0
              }
            }}
          />
          <TextField
            label="Device label"
            value={settings.account.deviceName}
            onChange={(event) =>
              setSettings((current) => ({
                ...current,
                account: {
                  ...current.account,
                  deviceName: event.target.value
                }
              }))
            }
            fullWidth
            size="small"
            sx={{
              mt: 1.25,
              '& .MuiOutlinedInput-root': {
                bgcolor: '#1f261c',
                color: '#f3f7df',
                borderRadius: 0
              }
            }}
          />
          <Box
            sx={{
              mt: 1.25,
              p: 1.25,
              border: '2px solid rgba(96, 117, 87, 0.9)',
              bgcolor: '#1f261c'
            }}
          >
            <Typography variant="caption" sx={{ color: '#a5b39a', display: 'block' }}>
              Mesh node identity
            </Typography>
            <Typography variant="body2" sx={{ mt: 0.4, color: '#f5e6a6', fontFamily: 'var(--font-code)' }}>
              {settings.account.nodeId}
            </Typography>
            <Typography variant="caption" sx={{ mt: 0.75, display: 'block', color: '#94a3b8' }}>
              Protocol {settings.mesh.protocolVersion} | {settings.mesh.trustMode}
            </Typography>
          </Box>
          <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mt: 1.25 }}>
            <Button
              onClick={() => {
                void handleExportProfile();
              }}
              startIcon={<UploadFile />}
              sx={{
                color: '#f3f7df',
                border: '2px solid rgba(96, 117, 87, 0.9)',
                bgcolor: '#1f261c'
              }}
            >
              Export Backup
            </Button>
            <Button
              onClick={() => {
                void handleImportProfile();
              }}
              startIcon={<Download />}
              sx={{
                color: '#f3f7df',
                border: '2px solid rgba(96, 117, 87, 0.9)',
                bgcolor: '#1f261c'
              }}
            >
              Import Backup
            </Button>
            <Button
              onClick={() => {
                void handleCopyMeshIdentity();
              }}
              startIcon={<Hub />}
              sx={{
                color: '#f3f7df',
                border: '2px solid rgba(96, 117, 87, 0.9)',
                bgcolor: '#1f261c'
              }}
            >
              Copy Node ID
            </Button>
          </Stack>
        </Box>

        <Divider sx={{ my: 2, borderColor: 'rgba(96, 117, 87, 0.75)' }} />

        <Box>
          <Stack direction="row" spacing={1} alignItems="center">
            <Shield fontSize="small" sx={{ color: '#f4ba3f' }} />
            <Typography variant="subtitle2" sx={{ color: '#f5e6a6' }}>
              Signed Updates
            </Typography>
          </Stack>
          <Typography variant="body2" sx={{ mt: 1, color: '#c7d0b1' }}>
            WaterFall verifies signed release manifests in the main process, stages verified
            artifacts locally, and records rollback posture before any rollout handoff.
          </Typography>
          <Box
            sx={{
              mt: 1.25,
              p: 1.25,
              border: '2px solid rgba(96, 117, 87, 0.9)',
              bgcolor: '#1f261c'
            }}
          >
            <Typography variant="caption" sx={{ color: '#a5b39a', display: 'block' }}>
              Updater status
            </Typography>
            <Typography variant="body2" sx={{ mt: 0.4, color: '#f5e6a6' }}>
              {updatesLoading
                ? 'Checking signed release lane...'
                : updateManifest?.statusMessage ||
                  updateError ||
                  'WaterFall has not checked the updater lane yet.'}
            </Typography>
            <Typography variant="caption" sx={{ mt: 0.75, display: 'block', color: '#94a3b8' }}>
              Integrity {updateManifest?.integrityState || 'unknown'} | Stage{' '}
              {updateManifest?.stageStatus || 'idle'} | Rollback{' '}
              {updateManifest?.rollbackReady ? 'ready' : 'not staged'}
            </Typography>
            {updateManifest?.artifactSha256 && (
              <Typography
                variant="caption"
                sx={{ mt: 0.75, display: 'block', color: '#94a3b8', fontFamily: 'var(--font-code)' }}
              >
                {updateManifest.artifactName || 'artifact'} | {updateManifest.artifactSha256}
              </Typography>
            )}
          </Box>
          <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mt: 1.25 }}>
            <Button
              onClick={() => {
                void refreshUpdateManifest();
              }}
              startIcon={<Refresh />}
              sx={{
                color: '#f3f7df',
                border: '2px solid rgba(96, 117, 87, 0.9)',
                bgcolor: '#1f261c'
              }}
            >
              Check Updates
            </Button>
            <Button
              onClick={() => {
                void handleApplyUpdate();
              }}
              disabled={
                updatesLoading ||
                !updateManifest ||
                !updateManifest.available ||
                updateManifest.integrityState !== 'verified'
              }
              startIcon={<Download />}
              sx={{
                color: '#f3f7df',
                border: '2px solid rgba(96, 117, 87, 0.9)',
                bgcolor: '#302414'
              }}
            >
              Stage Verified Update
            </Button>
            <Button
              onClick={() => navigateTab(activeTab.id, WATERFALL_UPDATES_ROUTE)}
              startIcon={<Launch />}
              sx={{
                color: '#f3f7df',
                border: '2px solid rgba(96, 117, 87, 0.9)',
                bgcolor: '#1f261c'
              }}
            >
              Open Update Deck
            </Button>
          </Stack>
        </Box>

        <Divider sx={{ my: 2, borderColor: 'rgba(96, 117, 87, 0.75)' }} />

        <Box>
          <Stack direction="row" spacing={1} alignItems="center">
            <Shield fontSize="small" sx={{ color: '#7dd3fc' }} />
            <Typography variant="subtitle2" sx={{ color: '#f5e6a6' }}>
              Security Workbench
            </Typography>
          </Stack>
          <Typography variant="body2" sx={{ mt: 1, color: '#c7d0b1' }}>
            Download Gate now runs preflight and postflight scans in the browser lifecycle, with
            quarantine and evidence export available from WaterFall itself.
          </Typography>
          <Box
            sx={{
              mt: 1.25,
              p: 1.25,
              border: '2px solid rgba(96, 117, 87, 0.9)',
              bgcolor: '#1f261c'
            }}
          >
            <Typography variant="caption" sx={{ color: '#a5b39a', display: 'block' }}>
              Security queue
            </Typography>
            <Typography variant="body2" sx={{ mt: 0.4, color: '#f5e6a6' }}>
              {securitySummary.totalDownloads} tracked | {securitySummary.clean} clean |{' '}
              {securitySummary.review} review | {securitySummary.quarantined} quarantined |{' '}
              {securitySummary.pending} pending
            </Typography>
            <Typography variant="caption" sx={{ mt: 0.75, display: 'block', color: '#94a3b8' }}>
              Orchestrator {securityStatus?.orchestratorMode || 'pending'} | Download Gate{' '}
              {securityStatus?.downloadGateOnline ? 'online' : 'offline'}
            </Typography>
          </Box>
          <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mt: 1.25 }}>
            <Button
              onClick={() => navigateTab(activeTab.id, WATERFALL_SECURITY_WORKBENCH_ROUTE)}
              startIcon={<Shield />}
              sx={{
                color: '#f3f7df',
                border: '2px solid rgba(96, 117, 87, 0.9)',
                bgcolor: '#1f261c'
              }}
            >
              Open Workbench
            </Button>
            <Button
              onClick={() => {
                void refreshSecurityStatus();
              }}
              startIcon={<Refresh />}
              sx={{
                color: '#f3f7df',
                border: '2px solid rgba(96, 117, 87, 0.9)',
                bgcolor: '#1f261c'
              }}
            >
              Refresh Security
            </Button>
            <Button
              onClick={() => {
                void handleExportSecurityReport();
              }}
              startIcon={<UploadFile />}
              sx={{
                color: '#f3f7df',
                border: '2px solid rgba(96, 117, 87, 0.9)',
                bgcolor: '#302414'
              }}
            >
              Export Report
            </Button>
            <Button
              onClick={() => navigateTab(activeTab.id, WATERFALL_PRIVACY_AUDITOR_ROUTE)}
              startIcon={<PrivacyTip />}
              sx={{
                color: '#f3f7df',
                border: '2px solid rgba(96, 117, 87, 0.9)',
                bgcolor: '#1f261c'
              }}
            >
              Privacy Auditor
            </Button>
            <Button
              onClick={() => navigateTab(activeTab.id, WATERFALL_SECURITY_ARCHITECT_ROUTE)}
              startIcon={<Shield />}
              sx={{
                color: '#f3f7df',
                border: '2px solid rgba(96, 117, 87, 0.9)',
                bgcolor: '#302414'
              }}
            >
              Security Architect
            </Button>
            <Button
              onClick={() => {
                void handleExportBountyPack();
              }}
              startIcon={<UploadFile />}
              sx={{
                color: '#f3f7df',
                border: '2px solid rgba(96, 117, 87, 0.9)',
                bgcolor: '#302414'
              }}
            >
              Export Bounty Pack
            </Button>
          </Stack>
        </Box>

        <Divider sx={{ my: 2, borderColor: 'rgba(96, 117, 87, 0.75)' }} />

        <Box>
          <Stack direction="row" spacing={1} alignItems="center">
            <Shield fontSize="small" sx={{ color: '#7dd3fc' }} />
            <Typography variant="subtitle2" sx={{ color: '#f5e6a6' }}>
              Browser Guardrails
            </Typography>
          </Stack>
          <Typography variant="body2" sx={{ mt: 1, color: '#c7d0b1' }}>
            WaterFall only opens http, https, and its own waterfall:// routes, strips guest
            preload hooks, keeps node integration off, and denies guest permission requests by
            default.
          </Typography>
        </Box>

        <Divider sx={{ my: 2, borderColor: 'rgba(96, 117, 87, 0.75)' }} />

        <Box>
          <Stack direction="row" spacing={1} alignItems="center">
            <PrivacyTip fontSize="small" sx={{ color: '#7dd3fc' }} />
            <Typography variant="subtitle2" sx={{ color: '#f5e6a6' }}>
              Privacy And Network
            </Typography>
          </Stack>
          <FormControlLabel
            sx={{ mt: 1.25 }}
            control={
              <Switch
                checked={settings.privacy.doNotTrack}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    privacy: {
                      ...current.privacy,
                      doNotTrack: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Send Do Not Track"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.privacy.globalPrivacyControl}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    privacy: {
                      ...current.privacy,
                      globalPrivacyControl: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Send Global Privacy Control"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.privacy.blockTrackers}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    privacy: {
                      ...current.privacy,
                      blockTrackers: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Block known tracker hosts"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.privacy.httpsOnlyMode}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    privacy: {
                      ...current.privacy,
                      httpsOnlyMode: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Upgrade public http routes to https"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.privacy.masterKillSwitch}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    privacy: {
                      ...current.privacy,
                      masterKillSwitch: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Arm the master kill switch for browser network traffic"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.privacy.permissionsLockdown}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    privacy: {
                      ...current.privacy,
                      permissionsLockdown: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Deny guest permission checks and prompts"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.privacy.stripReferrers}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    privacy: {
                      ...current.privacy,
                      stripReferrers: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Strip referrer headers"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.privacy.antiFingerprinting}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    privacy: {
                      ...current.privacy,
                      antiFingerprinting: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Apply anti-fingerprinting header shaping"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.privacy.blockPopups}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    privacy: {
                      ...current.privacy,
                      blockPopups: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Block guest popup windows"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.privacy.clearDataOnExit}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    privacy: {
                      ...current.privacy,
                      clearDataOnExit: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Clear WaterFall partition data on exit"
          />
          <TextField
            label="Blocked hosts"
            value={settings.privacy.blockedHosts.join(', ')}
            onChange={(event) =>
              setSettings((current) => ({
                ...current,
                privacy: {
                  ...current.privacy,
                  blockedHosts: event.target.value
                    .split(',')
                    .map((value) => value.trim())
                    .filter(Boolean)
                }
              }))
            }
            fullWidth
            size="small"
            sx={{
              mt: 1.25,
              '& .MuiOutlinedInput-root': {
                bgcolor: '#1f261c',
                color: '#f3f7df',
                borderRadius: 0
              }
            }}
          />
          <TextField
            select
            label="Proxy mode"
            value={settings.network.proxyMode}
            onChange={(event) =>
              setSettings((current) => ({
                ...current,
                network: {
                  ...current.network,
                  proxyMode: event.target.value as 'system' | 'manual'
                }
              }))
            }
            fullWidth
            size="small"
            sx={{
              mt: 1.25,
              '& .MuiOutlinedInput-root': {
                bgcolor: '#1f261c',
                color: '#f3f7df',
                borderRadius: 0
              }
            }}
          >
            <MenuItem value="system">System</MenuItem>
            <MenuItem value="manual">Manual</MenuItem>
          </TextField>
          <TextField
            label="Proxy rules"
            value={settings.network.proxyRules}
            onChange={(event) =>
              setSettings((current) => ({
                ...current,
                network: {
                  ...current.network,
                  proxyRules: event.target.value
                }
              }))
            }
            fullWidth
            size="small"
            disabled={settings.network.proxyMode !== 'manual'}
            sx={{
              mt: 1.25,
              '& .MuiOutlinedInput-root': {
                bgcolor: '#1f261c',
                color: '#f3f7df',
                borderRadius: 0
              }
            }}
          />
          <TextField
            label="Proxy bypass"
            value={settings.network.proxyBypassRules}
            onChange={(event) =>
              setSettings((current) => ({
                ...current,
                network: {
                  ...current.network,
                  proxyBypassRules: event.target.value
                }
              }))
            }
            fullWidth
            size="small"
            disabled={settings.network.proxyMode !== 'manual'}
            sx={{
              mt: 1.25,
              '& .MuiOutlinedInput-root': {
                bgcolor: '#1f261c',
                color: '#f3f7df',
                borderRadius: 0
              }
            }}
          />
        </Box>

        <Divider sx={{ my: 2, borderColor: 'rgba(96, 117, 87, 0.75)' }} />

        <Box>
          <Stack direction="row" spacing={1} alignItems="center">
            <Shield fontSize="small" sx={{ color: '#f4ba3f' }} />
            <Typography variant="subtitle2" sx={{ color: '#f5e6a6' }}>
              Download Gate
            </Typography>
          </Stack>
          <Typography variant="body2" sx={{ mt: 1, color: '#c7d0b1' }}>
            Control preflight inspection, postflight rescans, quarantine posture, and evidence
            export for WaterFall downloads.
          </Typography>
          <FormControlLabel
            sx={{ mt: 1.25 }}
            control={
              <Switch
                checked={settings.security.scanDownloadsOnStart}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    security: {
                      ...current.security,
                      scanDownloadsOnStart: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Scan downloads before writing to disk"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.security.scanDownloadsOnCompletion}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    security: {
                      ...current.security,
                      scanDownloadsOnCompletion: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Scan downloads after completion"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.security.quarantineHighRiskDownloads}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    security: {
                      ...current.security,
                      quarantineHighRiskDownloads: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Quarantine high-risk artifacts automatically"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.security.strictScopeMode}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    security: {
                      ...current.security,
                      strictScopeMode: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Keep workbench in strict authorized scope mode"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.security.nativeArtifactScanning}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    security: {
                      ...current.security,
                      nativeArtifactScanning: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Enable native artifact scanning"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.security.externalAuthorizedScanning}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    security: {
                      ...current.security,
                      externalAuthorizedScanning: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Enable explicitly authorized external scanning"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.security.exportEvidenceBundles}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    security: {
                      ...current.security,
                      exportEvidenceBundles: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Allow security report and evidence export"
          />
          <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mt: 1.25 }}>
            <Button
              onClick={() => navigateTab(activeTab.id, WATERFALL_SECURITY_WORKBENCH_ROUTE)}
              startIcon={<Shield />}
              sx={{
                color: '#f3f7df',
                border: '2px solid rgba(96, 117, 87, 0.9)',
                bgcolor: '#1f261c'
              }}
            >
              Open Workbench
            </Button>
            <Button
              onClick={() => {
                void handleExportSecurityReport();
              }}
              startIcon={<UploadFile />}
              sx={{
                color: '#f3f7df',
                border: '2px solid rgba(96, 117, 87, 0.9)',
                bgcolor: '#302414'
              }}
            >
              Export Report
            </Button>
          </Stack>
        </Box>

        <Divider sx={{ my: 2, borderColor: 'rgba(96, 117, 87, 0.75)' }} />

        <Box>
          <Stack direction="row" spacing={1} alignItems="center">
            <Extension fontSize="small" sx={{ color: '#f4ba3f' }} />
            <Typography variant="subtitle2" sx={{ color: '#f5e6a6' }}>
              Extension Deck
            </Typography>
          </Stack>
          <Typography variant="body2" sx={{ mt: 1, color: '#c7d0b1' }}>
            Load trusted unpacked extensions into WaterFall’s isolated session partition.
          </Typography>
          <Button
            onClick={() => {
              void handleAddExtension();
            }}
            startIcon={<Add />}
            sx={{
              mt: 1.25,
              color: '#f3f7df',
              border: '2px solid rgba(96, 117, 87, 0.9)',
              bgcolor: '#1f261c'
            }}
          >
            Add Extension
          </Button>
          <Stack spacing={1} sx={{ mt: 1.25 }}>
            {extensions.length === 0 && (
              <Typography variant="body2" sx={{ color: '#a5b39a' }}>
                No extensions loaded yet.
              </Typography>
            )}
            {extensions.map((extension) => (
              <Box
                key={`${extension.path}-${extension.id}`}
                sx={{
                  p: 1.25,
                  border: '2px solid rgba(96, 117, 87, 0.9)',
                  bgcolor: '#1f261c'
                }}
              >
                <Typography variant="body2">{extension.name}</Typography>
                <Typography variant="caption" sx={{ color: '#94a3b8', display: 'block' }}>
                  {extension.version || 'unversioned'} | {extension.path}
                </Typography>
                {extension.loadError && (
                  <Typography variant="caption" sx={{ color: '#fca5a5', display: 'block', mt: 0.5 }}>
                    {extension.loadError}
                  </Typography>
                )}
                <Button
                  onClick={() => {
                    void handleRemoveExtension(extension.path);
                  }}
                  size="small"
                  sx={{ mt: 0.75, color: '#f3f7df', borderRadius: 0 }}
                >
                  Remove
                </Button>
              </Box>
            ))}
          </Stack>
        </Box>

        <Divider sx={{ my: 2, borderColor: 'rgba(96, 117, 87, 0.75)' }} />

        <Box>
          <Stack direction="row" spacing={1} alignItems="center">
            <Bolt fontSize="small" sx={{ color: '#f4ba3f' }} />
            <Typography variant="subtitle2" sx={{ color: '#f5e6a6' }}>
              Collective Acceleration
            </Typography>
          </Stack>
          <Typography variant="body2" sx={{ mt: 1, color: '#c7d0b1' }}>
            Explicit, capped, and voluntary. This lays down the consent model for future mesh
            compute without pretending national-scale bandwidth appears by magic.
          </Typography>

          <FormControlLabel
            sx={{ mt: 1.25 }}
            control={
              <Switch
                checked={settings.collective.enabled}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    collective: {
                      ...current.collective,
                      enabled: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Allow WaterFall to join a future shared-compute mesh"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.collective.cpuEnabled}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    collective: {
                      ...current.collective,
                      cpuEnabled: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Share CPU capacity"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.collective.gpuEnabled}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    collective: {
                      ...current.collective,
                      gpuEnabled: event.target.checked
                    }
                  }))
                }
                disabled={!resourceProfile?.gpu.devices.length}
              />
            }
            label="Share GPU capacity"
          />

          <Box sx={{ mt: 1.25 }}>
            <Typography variant="caption" sx={{ color: '#a5b39a' }}>
              CPU cap: {settings.collective.cpuLimitPercent}%
            </Typography>
            <Slider
              value={settings.collective.cpuLimitPercent}
              min={5}
              max={90}
              step={5}
              onChange={(_event, value) =>
                setSettings((current) => ({
                  ...current,
                  collective: {
                    ...current.collective,
                    cpuLimitPercent: value as number
                  }
                }))
              }
            />
          </Box>

          <Box sx={{ mt: 1 }}>
            <Typography variant="caption" sx={{ color: '#a5b39a' }}>
              GPU cap: {settings.collective.gpuLimitPercent}%
            </Typography>
            <Slider
              value={settings.collective.gpuLimitPercent}
              min={5}
              max={90}
              step={5}
              onChange={(_event, value) =>
                setSettings((current) => ({
                  ...current,
                  collective: {
                    ...current.collective,
                    gpuLimitPercent: value as number
                  }
                }))
              }
              disabled={!resourceProfile?.gpu.devices.length}
            />
          </Box>

          <TextField
            label="Session cap (minutes)"
            type="number"
            value={settings.collective.sessionCapMinutes}
            onChange={(event) =>
              setSettings((current) => ({
                ...current,
                collective: {
                  ...current.collective,
                  sessionCapMinutes: Math.max(5, Number(event.target.value) || 5)
                }
              }))
            }
            fullWidth
            size="small"
            sx={{
              mt: 1.25,
              '& .MuiOutlinedInput-root': {
                bgcolor: '#1f261c',
                color: '#f3f7df',
                borderRadius: 0
              }
            }}
          />

          <FormControlLabel
            sx={{ mt: 1.25 }}
            control={
              <Switch
                checked={settings.collective.requireIdle}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    collective: {
                      ...current.collective,
                      requireIdle: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Only contribute while the workstation is idle"
          />
          <FormControlLabel
            control={
              <Switch
                checked={settings.collective.requireAC}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    collective: {
                      ...current.collective,
                      requireAC: event.target.checked
                    }
                  }))
                }
              />
            }
            label="Require AC power"
          />

          {resourceProfile && (
            <Stack spacing={1} sx={{ mt: 1.5 }}>
              <Chip
                label={`${resourceProfile.cpu.cores} CPU cores at ${resourceProfile.cpu.speedMhz} MHz`}
                size="small"
                sx={{ color: '#7dd3fc', justifyContent: 'flex-start' }}
              />
              <Chip
                label={`${resourceProfile.memory.totalGb} GB RAM | ${resourceProfile.memory.freeGb} GB free`}
                size="small"
                sx={{ color: '#c4b5fd', justifyContent: 'flex-start' }}
              />
              <Chip
                label={
                  resourceProfile.gpu.devices.length
                    ? `${resourceProfile.gpu.devices.length} GPU device(s) detected`
                    : 'No GPU device surfaced by Electron'
                }
                size="small"
                sx={{ color: '#fbbf24', justifyContent: 'flex-start' }}
              />
            </Stack>
          )}

          <Box
            sx={{
              mt: 1.5,
              p: 1.25,
              border: '2px solid rgba(96, 117, 87, 0.9)',
              bgcolor: '#1f261c'
            }}
          >
            <Typography variant="body2" sx={{ color: '#f5e6a6', fontWeight: 700 }}>
              Planning estimate
            </Typography>
            <Typography variant="body2" sx={{ mt: 0.75, color: '#c7d0b1' }}>
              Local pledge: {collectiveProjection.localUnits} WaterFall units.
            </Typography>
            <Stack spacing={0.6} sx={{ mt: 1 }}>
              {collectiveProjection.projections.map((projection) => (
                <Typography key={projection.participants} variant="caption" sx={{ color: '#a5b39a' }}>
                  {projection.participants} matched participants: {projection.units} units
                </Typography>
              ))}
            </Stack>
          </Box>
        </Box>

        <Divider sx={{ my: 2, borderColor: 'rgba(96, 117, 87, 0.75)' }} />

        <Box>
          <Stack direction="row" spacing={1} alignItems="center">
            <Download fontSize="small" sx={{ color: '#f4ba3f' }} />
            <Typography variant="subtitle2" sx={{ color: '#f5e6a6' }}>
              Download Hangar
            </Typography>
          </Stack>
          <Stack spacing={1} sx={{ mt: 1.25 }}>
            {downloads.length === 0 && (
              <Typography variant="body2" sx={{ color: '#a5b39a' }}>
                No downloads recorded in this session yet.
              </Typography>
            )}
            {downloads.slice(0, 6).map((download) => (
              <Box
                key={download.id}
                sx={{
                  p: 1.25,
                  border: '2px solid rgba(96, 117, 87, 0.9)',
                  bgcolor: '#1f261c'
                }}
              >
                <Typography variant="body2">{download.filename}</Typography>
                <Typography variant="caption" sx={{ color: '#94a3b8', display: 'block' }}>
                  {download.status} | {Math.round(download.receivedBytes / 1024)} KB of{' '}
                  {Math.max(1, Math.round(download.totalBytes / 1024))} KB
                </Typography>
                <Button
                  onClick={() => {
                    void handleShowDownload(download.filePath);
                  }}
                  size="small"
                  sx={{ mt: 0.75, color: '#f3f7df', borderRadius: 0 }}
                >
                  Show In Folder
                </Button>
              </Box>
            ))}
          </Stack>
        </Box>

        <Divider sx={{ my: 2, borderColor: 'rgba(96, 117, 87, 0.75)' }} />

        <Box>
          <Typography variant="subtitle2" sx={{ color: '#f5e6a6' }}>
            Session Controls
          </Typography>
          <Stack direction="row" spacing={1} sx={{ mt: 1.25 }}>
            <Button
              onClick={handleResetSession}
              sx={{
                color: '#f3f7df',
                border: '2px solid rgba(96, 117, 87, 0.9)',
                bgcolor: '#1f261c'
              }}
            >
              Reset Session
            </Button>
              <Button
                onClick={handleClearHistory}
                sx={{
                  color: '#f3f7df',
                  border: '2px solid rgba(96, 117, 87, 0.9)',
                  bgcolor: '#1f261c'
              }}
            >
              Clear History
            </Button>
          </Stack>
        </Box>
      </Drawer>
    </Box>
  );
};

export default WaterfallBrowser;
