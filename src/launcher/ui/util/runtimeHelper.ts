export function initRuntime() {
  window.addEventListener("keydown", (ev) => {
    // capture F12 to open devtools
    // this is keydown instead of keypress since this key will stopPropagation in keydown so it will not trigger keypress
    if (ev.key === "F12") {
      (window as any).toggleDevTools(); // this is provided in preload.ts
    }
  });

  window.addEventListener("keydown", (ev) => {
    // capture ctrl+F5 or cmd+F5 to reload
    // this is keydown instead of keypress since this key will stopPropagation in keydown so it will not trigger keypress
    if ((ev.ctrlKey || ev.metaKey) && ev.key === "F5") {
      window.location.href = window.location.href;
    }
  });
}

export function getTitleBarRect() {
  return (window as any).navigator.windowControlsOverlay.getTitlebarAreaRect() as DOMRect; // this is provided by electron
}

export const platform = (window as any).platform as string;

const windowEventsFromElectron = (window as any).windowEvents as {
  // this is defined in preload.ts
  maximize: {
    on: (listener: () => void) => void;
    removeEventListener: (listener: () => void) => void;
  };
  unmaximize: {
    on: (listener: () => void) => void;
    removeEventListener: (listener: () => void) => void;
  };
  enterFullScreen: {
    on: (listener: () => void) => void;
    removeEventListener: (listener: () => void) => void;
  };
  leaveFullScreen: {
    on: (listener: () => void) => void;
    removeEventListener: (listener: () => void) => void;
  };
};

export const windowEvents = {
  ...windowEventsFromElectron,

  sizeChanged: {
    on: (listener: () => void) => {
      window.addEventListener("resize", listener);
      windowEventsFromElectron.maximize.on(listener);
      windowEventsFromElectron.unmaximize.on(listener);
      windowEventsFromElectron.enterFullScreen.on(listener);
      windowEventsFromElectron.leaveFullScreen.on(listener);
    },
    removeEventListener: (listener: () => void) => {
      window.removeEventListener("resize", listener);
      windowEventsFromElectron.maximize.removeEventListener(listener);
      windowEventsFromElectron.unmaximize.removeEventListener(listener);
      windowEventsFromElectron.enterFullScreen.removeEventListener(listener);
      windowEventsFromElectron.leaveFullScreen.removeEventListener(listener);
    },
  },
};
