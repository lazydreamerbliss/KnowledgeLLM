export { TypeApi } from "./api";

export interface Environments {
  osCode: NodeJS.Platform;
  osVersion: string;
  chromeVersion: string;
  nodeVersion: string;
  electronVersion: string;
  culture: string;
  characterSet: string;
}

export enum FsAccessMode {
  F_OK = 0,
  X_OK = 1 << 0,
  W_OK = 1 << 1,
  R_OK = 1 << 2,
}

// for more information, check https://nodejs.org/api/fs.html#file-system-flags
export enum FsOpenMode {
  r = "r",
  rPlus = "r+",
  rsPlus = "rs+",
  w = "w",
  wx = "wx",
  wPlus = "w+",
  wxPlus = "wx+",
  a = "a",
  ax = "ax",
  aPlus = "a+",
  axPlus = "ax+",
}
