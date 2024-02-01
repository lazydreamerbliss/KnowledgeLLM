import fs from "fs/promises";

function fsAccess(path: string, mode?: number) {
  return fs.access(path, fs.constants.F_OK);
}

function fsMkdir(path: string, mode?: number) {
  return fs.mkdir(path, {
    recursive: true,
    mode: mode ? mode : 0o777,
  });
}

export default function provideFsPromise() {
  return {
    fsAccess,
    fsMkdir,
  };
}
