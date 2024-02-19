const { contextBridge, ipcRenderer } = require("electron/renderer");
contextBridge.exposeInMainWorld("toggleDevTools", () => ipcRenderer.send("toggle-dev-tools"));
contextBridge.exposeInMainWorld("platform", process.platform);

contextBridge.exposeInMainWorld("windowEvents", {
  maximize: {
    on: (listener: () => void) => ipcRenderer.on("maximize", listener),
    removeEventListener: (listener: () => void) => ipcRenderer.removeListener("maximize", listener),
  },
  unmaximize: {
    on: (listener: () => void) => ipcRenderer.on("unmaximize", listener),
    removeEventListener: (listener: () => void) => ipcRenderer.removeListener("unmaximize", listener),
  },
  enterFullScreen: {
    on: (listener: () => void) => ipcRenderer.on("enter-full-screen", listener),
    removeEventListener: (listener: () => void) => ipcRenderer.removeListener("enter-full-screen", listener),
  },
  leaveFullScreen: {
    on: (listener: () => void) => ipcRenderer.on("leave-full-screen", listener),
    removeEventListener: (listener: () => void) => ipcRenderer.removeListener("leave-full-screen", listener),
  },
});
