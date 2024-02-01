import { TypeApi as OriginalApiType } from "../../backend/bridge/bridgeTypes"; // here we just import the type, so we actually did not import anything after the code is compiled

window.addEventListener("keydown", (ev) => {
  // this is keydown instead of keypress since this key will stopPropagation in keydown so it will not trigger keypress
  if (ev.key === "F12") {
    (window as any).toggleDevTools();
  }
});

type Promisify<T> = {
  [K in keyof T]: T[K] extends (...args: infer A) => infer R
    ? R extends Promise<any>
      ? (...args: A) => R
      : (...args: A) => Promise<R>
    : T[K];
};

type TypeApi = Promisify<OriginalApiType>;

const bridge = (window as any).bridge as {
  getApi: () => Promise<string[]>;
  callApi: (apiName: string, args: any[]) => Promise<{ error: string } | { data: any }>;
};

const host = {} as TypeApi;

(async function initApi() {
  const hostToInit = host as any;
  console.log("Loading API...");
  const apiMethods: string[] = await bridge.getApi();
  console.log("Full list of api methods: ", apiMethods);
  apiMethods.forEach((apiName) => {
    hostToInit[apiName] = async (...args: any[]) => {
      const result = await bridge.callApi(apiName, args);
      if ("error" in result) {
        throw result.error;
      }
      return result.data;
    };
  });
  console.log("API loaded");
})();

export default host;
