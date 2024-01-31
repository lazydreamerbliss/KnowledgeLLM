import { ipcMain } from "electron";
import Api from "./api";

export function loadApi() {
  console.log("Loading API...");
  const api = Api();

  const apiKeys = Object.keys(api);

  console.log("Full list of api methods: ", apiKeys);

  ipcMain.handle("get-api", () => apiKeys);

  ipcMain.handle("call-api", async (event, apiName, args): Promise<{ error: Error } | { data: any }> => {
    try {
      if (!apiName) {
        const error = new Error("No api name provided");
        console.error(error.message);
        return { error };
      }
      if (!apiKeys.includes(apiName)) {
        const error = new Error(`Api ${apiName} not found`);
        console.error(error.message);
        return { error };
      }
      return { data: await (api as any)[apiName](...args) };
    } catch (e) {
      const error = e as Error;
      console.error("Invoke api error:", error);
      return {
        error: new Error(),
      };
    }
  });
  console.log("API loaded");
}
