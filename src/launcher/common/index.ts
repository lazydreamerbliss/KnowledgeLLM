export async function Sleep(ms: number) {
  return new Promise<void>((resolve) => {
    setTimeout(() => {
      resolve();
    }, ms);
  });
}

export { v4 as randomUUID } from "uuid"; // randomUUID is not available here, so use package uuid instead

export function jsonStringify(obj: any) {
  // just json stringify, but prettier
  return JSON.stringify(obj, null, 2);
}
