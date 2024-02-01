import { Environments } from "./bridge/bridgeTypes";

const { contextBridge, ipcRenderer } = require("electron/renderer");

contextBridge.exposeInMainWorld("bridge", {
  getApi: () => ipcRenderer.invoke("get-api"),
  callApi: (apiName: string, args: any[]) => ipcRenderer.invoke("call-api", apiName, args),
});

contextBridge.exposeInMainWorld(
  "environments",
  (() => {
    const environments: Environments = {
      osCode: process.platform,
      osVersion: process.getSystemVersion(),
      chromeVersion: process.versions.chrome,
      nodeVersion: process.versions.node,
      electronVersion: process.versions.electron,
      culture: process.env.LANG ? process.env.LANG.split(".")[0] : "en",
      characterSet: process.env.LANG ? process.env.LANG.split(".")[1] : "UTF-8",
    };
    return environments;
  })()
);

contextBridge.exposeInMainWorld(
  "userDataPath",
  (() => {
    switch (process.platform) {
      case "win32":
        return process.env.AppData;
      case "darwin":
        return process.env.HOME + "/Library/Application Support";
      case "linux":
        return process.env.HOME + "/.config";
      default:
        return process.cwd(); // just put the config in current directory
    }
  })()
);

contextBridge.exposeInMainWorld("toggleDevTools", () => ipcRenderer.invoke("toggle-dev-tools"));
