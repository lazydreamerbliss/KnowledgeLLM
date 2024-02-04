import path from "node:path";

import { app, BrowserWindow, ipcMain } from "electron";
import { startServer } from "./serverDaemon";

startServer();

const createWindow = () => {
  const mainWindow = new BrowserWindow({
    minWidth: 800,
    minHeight: 600,
    width: 1366,
    height: 768,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: true,
    },
    backgroundColor: "#2e2c29",
  });
  mainWindow.setMenuBarVisibility(false);
  mainWindow.loadURL("http://localhost:5012");
  console.log(app.getLocale());
};

app.whenReady().then(() => {
  createWindow();
  ipcMain.on("minimize", (event) => {
    console.log(event);
    const webContents = event.sender;
    const win = BrowserWindow.fromWebContents(webContents);
    if (win === null) return;
    win.minimize();
  });
  ipcMain.on("set-title", (event, title) => {
    console.log("set-title called: ", title);
    const webContents = event.sender;
    const win = BrowserWindow.fromWebContents(webContents);
    if (win === null) return;
    win.setTitle(title);
  });
  ipcMain.handle("toggle-dev-tools", (event) => {
    const webContents = event.sender;
    webContents.toggleDevTools();
  });
});
