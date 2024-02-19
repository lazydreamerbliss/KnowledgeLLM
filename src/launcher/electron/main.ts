import path from "node:path";

import { app, BrowserWindow, ipcMain } from "electron";
import { startServer } from "./serverDaemon";
import windowStateKeeper from "electron-window-state";

startServer(); //start backend server first

const createWindow = () => {
  const mainWindowStateKeeper = windowStateKeeper({
    defaultWidth: 1366,
    defaultHeight: 768,
  });

  const mainWindow = new BrowserWindow({
    minWidth: 1280,
    minHeight: 720,
    width: mainWindowStateKeeper.width,
    height: mainWindowStateKeeper.height,
    x: mainWindowStateKeeper.x,
    y: mainWindowStateKeeper.y,
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
  mainWindowStateKeeper.manage(mainWindow);
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
  mainWindow.on("enter-full-screen", () => {
    mainWindow.webContents.send("enter-full-screen");
  });
  mainWindow.on("leave-full-screen", () => {
    mainWindow.webContents.send("leave-full-screen");
  });
};

app.whenReady().then(() => {
  createWindow();
  ipcMain.on("toggle-dev-tools", (event) => {
    const webContents = event.sender;
    webContents.toggleDevTools();
  });
});
