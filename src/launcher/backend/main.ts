import path from "node:path";

import { app, BrowserWindow } from "electron";

const createWindow = () => {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
    },
  });
  win.setMenuBarVisibility(false);

  win.webContents.openDevTools(); // Open the developer tools, for debugging
  //   win.loadFile("http://localhost");
  win.loadURL("http://localhost:5012");
};

app.whenReady().then(() => {
  createWindow();
});
