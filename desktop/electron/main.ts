import { app, BrowserWindow, ipcMain } from 'electron';
import { spawn, type ChildProcessWithoutNullStreams } from 'child_process';
import { promises as fs } from 'fs';
import * as path from 'path';
import { randomUUID } from 'crypto';
import Store from 'electron-store';

const store = new Store();
const FILE_SIZE_LIMIT_BYTES = 1024 * 1024;
const SEARCH_RESULT_LIMIT = 80;
const WINDOW_STATE_KEY = 'sovereign.ide.window-state';
const IGNORED_DIRECTORY_NAMES = new Set([
  '.git',
  '.hypothesis',
  '.mypy_cache',
  '.venv',
  '.venv_prod',
  '__pycache__',
  'build',
  'dist',
  'node_modules',
  'release'
]);

let mainWindow: BrowserWindow | null = null;
const terminalSessions = new Map<string, ChildProcessWithoutNullStreams>();

const getWorkspaceRoot = () => path.resolve(app.getAppPath(), '..');

const normalizeResolvedPath = (value: string) => path.resolve(value).replace(/[\\/]+$/, '').toLowerCase();

const resolveWorkspacePath = (targetPath = '') => {
  const workspaceRoot = getWorkspaceRoot();
  const resolvedPath = path.isAbsolute(targetPath)
    ? path.resolve(targetPath)
    : path.resolve(workspaceRoot, targetPath);
  const normalizedRoot = normalizeResolvedPath(workspaceRoot);
  const normalizedResolvedPath = normalizeResolvedPath(resolvedPath);

  if (
    normalizedResolvedPath !== normalizedRoot &&
    !normalizedResolvedPath.startsWith(`${normalizedRoot}${path.sep}`)
  ) {
    throw new Error('Requested path is outside the workspace root.');
  }

  return resolvedPath;
};

const isDirectoryIgnored = (directoryName: string) => IGNORED_DIRECTORY_NAMES.has(directoryName);

const sortWorkspaceEntries = <T extends { kind: 'file' | 'directory'; name: string }>(entries: T[]) =>
  entries.sort((left, right) => {
    if (left.kind !== right.kind) {
      return left.kind === 'directory' ? -1 : 1;
    }

    return left.name.localeCompare(right.name);
  });

async function listWorkspaceDirectory(targetPath = '') {
  const directoryPath = resolveWorkspacePath(targetPath);
  const entries = await fs.readdir(directoryPath, {
    withFileTypes: true
  });

  const mappedEntries = await Promise.all(
    entries
      .filter((entry) => !entry.isDirectory() || !isDirectoryIgnored(entry.name))
      .map(async (entry) => {
        const entryPath = path.join(directoryPath, entry.name);
        const stats = await fs.stat(entryPath);

        return {
          name: entry.name,
          path: entryPath,
          kind: (entry.isDirectory() ? 'directory' : 'file') as 'directory' | 'file',
          extension: entry.isDirectory() ? '' : path.extname(entry.name).toLowerCase(),
          size: stats.size,
          modifiedAt: stats.mtimeMs
        };
      })
  );

  return sortWorkspaceEntries(mappedEntries);
}

async function searchWorkspaceFiles(query: string) {
  const trimmedQuery = query.trim().toLowerCase();
  if (!trimmedQuery) {
    return [];
  }

  const workspaceRoot = getWorkspaceRoot();
  const queue = [workspaceRoot];
  const results: Array<{
    name: string;
    path: string;
    kind: 'file';
    extension: string;
    size: number;
    modifiedAt: number;
  }> = [];

  while (queue.length > 0 && results.length < SEARCH_RESULT_LIMIT) {
    const nextDirectory = queue.shift();
    if (!nextDirectory) {
      break;
    }

    let entries;
    try {
      entries = await fs.readdir(nextDirectory, {
        withFileTypes: true
      });
    } catch {
      continue;
    }

    for (const entry of entries) {
      const entryPath = path.join(nextDirectory, entry.name);

      if (entry.isDirectory()) {
        if (!isDirectoryIgnored(entry.name)) {
          queue.push(entryPath);
        }
        continue;
      }

      if (!entry.name.toLowerCase().includes(trimmedQuery) && !entryPath.toLowerCase().includes(trimmedQuery)) {
        continue;
      }

      const stats = await fs.stat(entryPath);
      results.push({
        name: entry.name,
        path: entryPath,
        kind: 'file',
        extension: path.extname(entry.name).toLowerCase(),
        size: stats.size,
        modifiedAt: stats.mtimeMs
      });

      if (results.length >= SEARCH_RESULT_LIMIT) {
        break;
      }
    }
  }

  return results;
}

async function readWorkspaceFile(targetPath: string) {
  const resolvedPath = resolveWorkspacePath(targetPath);
  const stats = await fs.stat(resolvedPath);
  const tooLarge = stats.size > FILE_SIZE_LIMIT_BYTES;

  if (tooLarge) {
    return {
      path: resolvedPath,
      content: '',
      isBinary: false,
      tooLarge: true,
      size: stats.size,
      modifiedAt: stats.mtimeMs
    };
  }

  const contentBuffer = await fs.readFile(resolvedPath);
  const isBinary = contentBuffer.subarray(0, Math.min(contentBuffer.length, 2048)).includes(0);

  return {
    path: resolvedPath,
    content: isBinary ? '' : contentBuffer.toString('utf8'),
    isBinary,
    tooLarge: false,
    size: stats.size,
    modifiedAt: stats.mtimeMs
  };
}

async function writeWorkspaceFile(targetPath: string, content: string) {
  const resolvedPath = resolveWorkspacePath(targetPath);
  const temporaryPath = `${resolvedPath}.tmp-${process.pid}-${Date.now()}`;
  await fs.writeFile(temporaryPath, content, 'utf8');
  await fs.rename(temporaryPath, resolvedPath);
  return readWorkspaceFile(resolvedPath);
}

function getStoredWindowBounds() {
  const storedValue = store.get(WINDOW_STATE_KEY);
  if (!storedValue || typeof storedValue !== 'object') {
    return {};
  }

  const candidate = storedValue as Record<string, unknown>;
  const numericKeys = ['x', 'y', 'width', 'height'] as const;

  return numericKeys.reduce<Record<string, number>>((current, key) => {
    const value = candidate[key];
    if (typeof value === 'number' && Number.isFinite(value)) {
      current[key] = value;
    }
    return current;
  }, {});
}

function persistWindowBounds() {
  if (!mainWindow || mainWindow.isMinimized() || mainWindow.isMaximized()) {
    return;
  }

  store.set(WINDOW_STATE_KEY, mainWindow.getBounds());
}

async function readGitStatus() {
  return await new Promise<string>((resolve, reject) => {
    const gitStatus = spawn('git', ['status', '--short', '--branch'], {
      cwd: getWorkspaceRoot(),
      stdio: ['ignore', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';

    gitStatus.stdout.on('data', (chunk) => {
      stdout += chunk.toString();
    });

    gitStatus.stderr.on('data', (chunk) => {
      stderr += chunk.toString();
    });

    gitStatus.on('error', reject);
    gitStatus.on('close', (code) => {
      if (code === 0) {
        resolve(stdout);
        return;
      }

      reject(new Error(stderr.trim() || `git status exited with code ${code}`));
    });
  });
}

async function getRepoStatus() {
  const rawStatus = await readGitStatus();
  const lines = rawStatus
    .split(/\r?\n/)
    .map((line) => line.trimEnd())
    .filter(Boolean);
  const branchLine = lines[0] || '## detached';
  const summaryLines = lines.slice(1);
  const conflictedCodes = new Set(['DD', 'AU', 'UD', 'UA', 'DU', 'AA', 'UU']);

  let modifiedCount = 0;
  let untrackedCount = 0;
  let conflictedCount = 0;

  for (const line of summaryLines) {
    const code = line.slice(0, 2);
    if (code === '??') {
      untrackedCount += 1;
    } else if (conflictedCodes.has(code)) {
      conflictedCount += 1;
    } else {
      modifiedCount += 1;
    }
  }

  return {
    branch: branchLine.replace(/^##\s*/, ''),
    modifiedCount,
    untrackedCount,
    conflictedCount,
    clean: summaryLines.length === 0,
    summary: summaryLines
  };
}

const sendTerminalData = (sessionId: string, stream: 'stdout' | 'stderr', data: string) => {
  mainWindow?.webContents.send('terminal:data', {
    id: sessionId,
    stream,
    data
  });
};

const sendTerminalExit = (sessionId: string, code: number | null) => {
  mainWindow?.webContents.send('terminal:exit', {
    id: sessionId,
    code
  });
};

function createTerminalSession() {
  const sessionId = randomUUID();
  const workspaceRoot = getWorkspaceRoot();
  const shellExecutable = process.platform === 'win32' ? 'pwsh.exe' : process.env.SHELL || 'bash';
  const shellArguments = process.platform === 'win32' ? ['-NoLogo', '-NoExit'] : [];
  const session = spawn(shellExecutable, shellArguments, {
    cwd: workspaceRoot,
    env: {
      ...process.env,
      TERM: 'xterm-256color'
    },
    stdio: ['pipe', 'pipe', 'pipe']
  });

  terminalSessions.set(sessionId, session);

  session.stdout.on('data', (chunk) => {
    sendTerminalData(sessionId, 'stdout', chunk.toString());
  });

  session.stderr.on('data', (chunk) => {
    sendTerminalData(sessionId, 'stderr', chunk.toString());
  });

  session.on('error', (error) => {
    sendTerminalData(sessionId, 'stderr', `${error.message}\n`);
    sendTerminalExit(sessionId, null);
    terminalSessions.delete(sessionId);
  });

  session.on('close', (code) => {
    sendTerminalExit(sessionId, code);
    terminalSessions.delete(sessionId);
  });

  return {
    id: sessionId,
    cwd: workspaceRoot,
    shell: process.platform === 'win32' ? 'PowerShell' : path.basename(shellExecutable)
  };
}

function createWindow() {
  mainWindow = new BrowserWindow({
    ...getStoredWindowBounds(),
    width: 1600,
    height: 980,
    minWidth: 1320,
    minHeight: 840,
    backgroundColor: '#0d110d',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      preload: path.join(__dirname, 'preload.js')
    },
    titleBarStyle: 'hidden',
    frame: false,
    show: false
  });

  mainWindow.webContents.setWindowOpenHandler(() => ({
    action: 'deny'
  }));

  mainWindow.webContents.session.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [
          "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' http://localhost:5173;"
        ]
      }
    });
  });

  if (process.env.NODE_ENV === 'development') {
    void mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools({
      mode: 'detach'
    });
  } else {
    void mainWindow.loadFile(path.join(__dirname, '../../build/index.html'));
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
  mainWindow.on('resize', persistWindowBounds);
  mainWindow.on('move', persistWindowBounds);
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  for (const session of terminalSessions.values()) {
    session.kill();
  }

  terminalSessions.clear();

  if (process.platform !== 'darwin') {
    app.quit();
  }
});

ipcMain.handle('window:minimize', () => {
  mainWindow?.minimize();
});

ipcMain.handle('window:maximize', () => {
  if (mainWindow?.isMaximized()) {
    mainWindow.restore();
  } else {
    mainWindow?.maximize();
  }
});

ipcMain.handle('window:close', () => {
  mainWindow?.close();
});

ipcMain.handle('store:get', (_, key: string) => store.get(key));
ipcMain.handle('store:set', (_, key: string, value: unknown) => {
  store.set(key, value);
});

ipcMain.handle('app:version', () => app.getVersion());

ipcMain.handle('workspace:get-root', () => getWorkspaceRoot());
ipcMain.handle('workspace:get-repo-status', async () => await getRepoStatus());
ipcMain.handle('workspace:list-directory', async (_, targetPath?: string) => {
  return await listWorkspaceDirectory(targetPath);
});
ipcMain.handle('workspace:search-files', async (_, query: string) => {
  return await searchWorkspaceFiles(query);
});
ipcMain.handle('workspace:read-file', async (_, targetPath: string) => {
  return await readWorkspaceFile(targetPath);
});
ipcMain.handle('workspace:write-file', async (_, targetPath: string, content: string) => {
  return await writeWorkspaceFile(targetPath, content);
});

ipcMain.handle('terminal:create-session', () => createTerminalSession());
ipcMain.handle('terminal:write', (_, sessionId: string, input: string) => {
  const session = terminalSessions.get(sessionId);
  if (!session) {
    throw new Error('Terminal session not found.');
  }

  session.stdin.write(input.endsWith('\n') ? input : `${input}\n`);
});
ipcMain.handle('terminal:kill', (_, sessionId: string) => {
  const session = terminalSessions.get(sessionId);
  if (!session) {
    return;
  }

  session.kill();
  terminalSessions.delete(sessionId);
});
