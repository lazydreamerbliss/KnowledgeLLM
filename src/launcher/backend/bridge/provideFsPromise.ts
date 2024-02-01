import { OpenMode } from "fs";
import fs from "fs/promises";
import { FsOpenMode } from "./bridgeTypes";

function fsAccess(path: string, mode?: number) {
  return fs.access(path, fs.constants.F_OK);
}

function fsMkdir(path: string, mode?: number) {
  return fs.mkdir(path, {
    recursive: true,
    mode: mode ? mode : 0o777,
  });
}

function fsWriteFile(path: string, data: string, flag?: FsOpenMode) {
  return fs.writeFile(path, data, { flag });
}

function fsReadFile(path: string) {
  return fs.readFile(path, { encoding: "utf-8" });
}

export default function provideFsPromise() {
  return {
    fsAccess,
    fsMkdir,
    fsWriteFile,
    fsReadFile,
  };
}
