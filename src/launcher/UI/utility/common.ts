export { v4 as randomUUID } from "uuid"; // randomUUID is not available here, so use package uuid instead

export function jsonStringify(obj: any) {
  // just json stringify, but prettier
  return JSON.stringify(obj, null, 2);
}

window.addEventListener("keydown", (ev) => {
  // this is keydown instead of keypress since this key will stopPropagation in keydown so it will not trigger keypress
  if (ev.key === "F12") {
    (window as any).toggleDevTools();
  }
});
