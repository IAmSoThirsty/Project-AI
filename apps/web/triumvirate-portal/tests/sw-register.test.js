/* eslint-env node, jest */
/* global require, __dirname, describe, test, expect, beforeEach, afterEach */

const path = require('node:path');

const modulePath = path.resolve(__dirname, '..', 'js', 'sw-register.js');

function flushPromises() {
  return new Promise((resolve) => setImmediate(resolve));
}

function createDomNode() {
  return {
    style: {},
    addEventListener: jest.fn(),
    appendChild: jest.fn(),
    remove: jest.fn(),
    set textContent(value) {
      this._textContent = value;
    },
    get textContent() {
      return this._textContent;
    },
    set innerHTML(value) {
      this._innerHTML = value;
    },
    get innerHTML() {
      return this._innerHTML;
    }
  };
}

function setupHarness(options = {}) {
  const {
    withServiceWorker = true,
    registerReject = false,
    confirmResult = true,
    hasController = true
  } = options;

  const windowListeners = {};
  const serviceWorkerListeners = {};
  const registrationListeners = {};
  const workerListeners = {};
  const installButtonListeners = {};
  const dismissButtonListeners = {};

  const installButton = {
    addEventListener: jest.fn((eventName, callback) => {
      installButtonListeners[eventName] = callback;
    })
  };

  const dismissButton = {
    addEventListener: jest.fn((eventName, callback) => {
      dismissButtonListeners[eventName] = callback;
    })
  };

  const document = {
    head: {
      appendChild: jest.fn()
    },
    body: {
      appendChild: jest.fn()
    },
    createElement: jest.fn(() => createDomNode()),
    getElementById: jest.fn((id) => {
      if (id === 'install-btn') return installButton;
      if (id === 'install-dismiss') return dismissButton;
      return null;
    })
  };

  const window = {
    addEventListener: jest.fn((eventName, callback) => {
      windowListeners[eventName] = callback;
    }),
    location: {
      hostname: 'localhost',
      reload: jest.fn()
    },
    document
  };

  global.window = window;
  global.document = document;
  global.setInterval = jest.fn();
  global.confirm = jest.fn(() => confirmResult);

  let registration;
  let newWorker;
  let serviceWorker;

  if (withServiceWorker) {
    newWorker = {
      state: 'installed',
      postMessage: jest.fn(),
      addEventListener: jest.fn((eventName, callback) => {
        workerListeners[eventName] = callback;
      })
    };

    registration = {
      scope: '/the_triumvirate/',
      update: jest.fn(),
      installing: newWorker,
      addEventListener: jest.fn((eventName, callback) => {
        registrationListeners[eventName] = callback;
      })
    };

    serviceWorker = {
      register: jest.fn(() => (
        registerReject
          ? Promise.reject(new Error('registration failed'))
          : Promise.resolve(registration)
      )),
      controller: hasController ? {} : null,
      addEventListener: jest.fn((eventName, callback) => {
        serviceWorkerListeners[eventName] = callback;
      })
    };

    global.navigator = { serviceWorker };
  } else {
    global.navigator = {};
  }

  return {
    window,
    windowListeners,
    serviceWorker,
    serviceWorkerListeners,
    registration,
    registrationListeners,
    newWorker,
    workerListeners,
    document,
    installButtonListeners,
    dismissButtonListeners
  };
}

describe('sw-register browser lifecycle behavior', () => {
  beforeEach(() => {
    jest.resetModules();
  });

  afterEach(() => {
    delete global.window;
    delete global.document;
    delete global.navigator;
    delete global.confirm;
    jest.restoreAllMocks();
  });

  test('registers service worker on load and handles update acceptance flow', async () => {
    const harness = setupHarness({
      withServiceWorker: true,
      confirmResult: true,
      hasController: true
    });

    jest.spyOn(console, 'log').mockImplementation(() => {});
    jest.spyOn(console, 'error').mockImplementation(() => {});

    require(modulePath);

    expect(harness.windowListeners.load).toEqual(expect.any(Function));

    harness.windowListeners.load();
    await flushPromises();
    await flushPromises();

    expect(harness.serviceWorker.register).toHaveBeenCalledWith('/the_triumvirate/sw.js', {
      scope: '/the_triumvirate/'
    });
    expect(global.setInterval).toHaveBeenCalledWith(expect.any(Function), 60000);

    expect(harness.registrationListeners.updatefound).toEqual(expect.any(Function));
    harness.registrationListeners.updatefound();

    expect(harness.workerListeners.statechange).toEqual(expect.any(Function));
    harness.workerListeners.statechange();

    expect(global.confirm).toHaveBeenCalledWith('A new version is available! Reload to update?');
    expect(harness.newWorker.postMessage).toHaveBeenCalledWith({ type: 'SKIP_WAITING' });
    expect(harness.window.location.reload).toHaveBeenCalledTimes(1);

    expect(harness.serviceWorkerListeners.controllerchange).toEqual(expect.any(Function));
    harness.serviceWorkerListeners.controllerchange();
    expect(harness.window.location.reload).toHaveBeenCalledTimes(2);
  });

  test('does not refresh when update confirmation is declined', async () => {
    const harness = setupHarness({
      withServiceWorker: true,
      confirmResult: false,
      hasController: true
    });

    jest.spyOn(console, 'log').mockImplementation(() => {});
    jest.spyOn(console, 'error').mockImplementation(() => {});

    require(modulePath);

    harness.windowListeners.load();
    await flushPromises();
    await flushPromises();

    harness.registrationListeners.updatefound();
    harness.workerListeners.statechange();

    expect(global.confirm).toHaveBeenCalled();
    expect(harness.newWorker.postMessage).not.toHaveBeenCalled();
    expect(harness.window.location.reload).not.toHaveBeenCalled();
  });

  test('logs service worker registration errors', async () => {
    const harness = setupHarness({
      withServiceWorker: true,
      registerReject: true
    });

    const errorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    require(modulePath);

    harness.windowListeners.load();
    await flushPromises();
    await flushPromises();

    expect(errorSpy).toHaveBeenCalledWith(
      '❌ ServiceWorker registration failed:',
      expect.any(Error)
    );
  });

  test('registers install prompt listeners even when service worker is unavailable', () => {
    const harness = setupHarness({ withServiceWorker: false });

    require(modulePath);

    expect(harness.windowListeners.load).toBeUndefined();
    expect(harness.windowListeners.beforeinstallprompt).toEqual(expect.any(Function));
    expect(harness.windowListeners.appinstalled).toEqual(expect.any(Function));
  });

  test('handles install promotion click and dismissal interactions', async () => {
    const harness = setupHarness({ withServiceWorker: false });
    jest.spyOn(console, 'log').mockImplementation(() => {});

    require(modulePath);

    const installEvent = {
      preventDefault: jest.fn(),
      prompt: jest.fn(),
      userChoice: Promise.resolve({ outcome: 'accepted' })
    };

    harness.windowListeners.beforeinstallprompt(installEvent);
    expect(installEvent.preventDefault).toHaveBeenCalled();
    expect(harness.document.body.appendChild).toHaveBeenCalledTimes(1);
    expect(harness.installButtonListeners.click).toEqual(expect.any(Function));

    const firstBanner = harness.document.body.appendChild.mock.calls[0][0];
    await harness.installButtonListeners.click();
    await flushPromises();

    expect(installEvent.prompt).toHaveBeenCalled();
    expect(firstBanner.remove).toHaveBeenCalledTimes(1);

    const dismissEvent = {
      preventDefault: jest.fn(),
      prompt: jest.fn(),
      userChoice: Promise.resolve({ outcome: 'dismissed' })
    };

    harness.windowListeners.beforeinstallprompt(dismissEvent);
    const secondBanner = harness.document.body.appendChild.mock.calls[1][0];

    expect(harness.dismissButtonListeners.click).toEqual(expect.any(Function));
    harness.dismissButtonListeners.click();

    expect(secondBanner.remove).toHaveBeenCalledTimes(1);
  });

  test('does nothing on install click after app is already installed', async () => {
    const harness = setupHarness({ withServiceWorker: false });
    jest.spyOn(console, 'log').mockImplementation(() => {});

    require(modulePath);

    const installEvent = {
      preventDefault: jest.fn(),
      prompt: jest.fn(),
      userChoice: Promise.resolve({ outcome: 'accepted' })
    };

    harness.windowListeners.beforeinstallprompt(installEvent);
    harness.windowListeners.appinstalled();

    await harness.installButtonListeners.click();

    expect(installEvent.prompt).not.toHaveBeenCalled();
  });
});
