import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electron', {
  window: {
    minimize: () => ipcRenderer.invoke('window:minimize'),
    maximize: () => ipcRenderer.invoke('window:maximize'),
    close: () => ipcRenderer.invoke('window:close')
  },
  store: {
    get: (key: string) => ipcRenderer.invoke('store:get', key),
    set: (key: string, value: unknown) => ipcRenderer.invoke('store:set', key, value)
  },
  app: {
    getVersion: () => ipcRenderer.invoke('app:version')
  },
  workspace: {
    getRoot: () => ipcRenderer.invoke('workspace:get-root'),
    getRepoStatus: () => ipcRenderer.invoke('workspace:get-repo-status'),
    listDirectory: (targetPath?: string) => ipcRenderer.invoke('workspace:list-directory', targetPath),
    searchFiles: (query: string) => ipcRenderer.invoke('workspace:search-files', query),
    readFile: (targetPath: string) => ipcRenderer.invoke('workspace:read-file', targetPath),
    writeFile: (targetPath: string, content: string) =>
      ipcRenderer.invoke('workspace:write-file', targetPath, content)
  },
  terminal: {
    createSession: () => ipcRenderer.invoke('terminal:create-session'),
    write: (sessionId: string, input: string) => ipcRenderer.invoke('terminal:write', sessionId, input),
    kill: (sessionId: string) => ipcRenderer.invoke('terminal:kill', sessionId),
    onData: (handler: (event: unknown) => void) => {
      const listener = (_event: Electron.IpcRendererEvent, payload: unknown) => handler(payload);
      ipcRenderer.on('terminal:data', listener);
      return () => {
        ipcRenderer.removeListener('terminal:data', listener);
      };
    },
    onExit: (handler: (event: unknown) => void) => {
      const listener = (_event: Electron.IpcRendererEvent, payload: unknown) => handler(payload);
      ipcRenderer.on('terminal:exit', listener);
      return () => {
        ipcRenderer.removeListener('terminal:exit', listener);
      };
    }
  }
});
