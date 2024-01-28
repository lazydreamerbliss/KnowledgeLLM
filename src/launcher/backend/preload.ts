const { contextBridge, ipcRenderer } = require("electron/renderer");

contextBridge.exposeInMainWorld("bridge", {
  getApi: () => ipcRenderer.invoke("get-api"),
  callApi: (apiName: string, args: any[]) => ipcRenderer.invoke("call-api", apiName, args),
});
