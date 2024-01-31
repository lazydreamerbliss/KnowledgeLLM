import fs from "node:fs/promises";

async function fsAccess(path: string, mode?: number) {
  const result = await fs.access(path, fs.constants.F_OK);
  return result;
}

export default function provideFsPromise() {
  return {
    fsAccess,
  };
}
