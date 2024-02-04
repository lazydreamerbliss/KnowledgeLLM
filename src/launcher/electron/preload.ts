const { contextBridge, ipcRenderer } = require("electron/renderer");
contextBridge.exposeInMainWorld("toggleDevTools", () => ipcRenderer.invoke("toggle-dev-tools"));
