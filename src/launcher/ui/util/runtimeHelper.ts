export function initRuntime() {
  window.addEventListener("keydown", (ev) => {
    // capture F12 to open devtools
    // this is keydown instead of keypress since this key will stopPropagation in keydown so it will not trigger keypress
    if (ev.key === "F12") {
      (window as any).toggleDevTools();
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

export function getTitleBarRect(): DOMRect {
  return (window as any).navigator.windowControlsOverlay.getTitlebarAreaRect();
}
