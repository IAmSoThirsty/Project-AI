declare global {
  interface Window {
    electron?: {
      window: {
        minimize: () => Promise<void>;
        maximize: () => Promise<void>;
        close: () => Promise<void>;
      };
      store: {
        get: (key: string) => Promise<any>;
        set: (key: string, value: any) => Promise<void>;
      };
      app: {
        getVersion: () => Promise<string>;
      };
    };
  }
}

export {};
