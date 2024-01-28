import path from "node:path";

import { app, BrowserWindow, ipcMain } from "electron";
import { loadApi } from "./bridge/bridge-main";

const createWindow = () => {
  const mainWindow = new BrowserWindow({
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: true,
    },
  });
  mainWindow.setMenuBarVisibility(false);

  mainWindow.webContents.openDevTools({
    mode: "undocked",
    activate: false,
  }); // Open the developer tools, for debugging
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
  loadApi();
});
