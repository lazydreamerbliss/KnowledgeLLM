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
