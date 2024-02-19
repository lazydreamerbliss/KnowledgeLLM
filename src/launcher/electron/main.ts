import path from "node:path";

import { app, BrowserWindow, ipcMain, webContents } from "electron";
import { startServer } from "./serverDaemon";

startServer();

const createWindow = () => {
  const mainWindow = new BrowserWindow({
    minWidth: 1366,
    minHeight: 768,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: true,
    },
    backgroundColor: "#000000",
    titleBarStyle: "hidden",
    titleBarOverlay: {
      color: "#272727",
      symbolColor: "#dfdfdf",
      height: 32, // looks good both for MacOS and Windows
    },
  });
  mainWindow.setMenuBarVisibility(false);
  mainWindow.loadURL("http://localhost:5012");
  console.log(app.getLocale());
  // mainWindow.webContents.toggleDevTools();
  mainWindow.on("maximize", () => {
    mainWindow.webContents.send("maximize");
  });
  mainWindow.on("unmaximize", () => {
    mainWindow.webContents.send("unmaximize");
  });
};

app.whenReady().then(() => {
  createWindow();
  ipcMain.on("toggle-dev-tools", (event) => {
    const webContents = event.sender;
    webContents.toggleDevTools();
  });
});
