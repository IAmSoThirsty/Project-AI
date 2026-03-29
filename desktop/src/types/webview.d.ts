import type * as React from 'react';

declare global {
  namespace JSX {
    interface IntrinsicElements {
      webview: React.DetailedHTMLProps<
        React.HTMLAttributes<Electron.WebviewTag>,
        Electron.WebviewTag
      > & {
        allowpopups?: boolean | 'true' | 'false';
        partition?: string;
        src?: string;
        useragent?: string;
        webpreferences?: string;
      };
    }
  }
}

export {};
