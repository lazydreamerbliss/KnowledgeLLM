import { TypeApi as OriginalApiType } from "../../backend/bridge/bridgeTypes"; // here we just import the type, so we actually did not import anything after the code is compiled

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
  callApi: (apiName: string, args: any[]) => Promise<{ error: Error } | { data: any }>;
};

const host = {} as TypeApi;

(async function initApi() {
  const hostToInit = host as any;
  console.log("Loading API...");
  const apiMethods: string[] = await bridge.getApi();
  console.log("Full list of api methods: ", apiMethods);
  apiMethods.forEach((apiName) => {
    hostToInit[apiName] = async (...args: any[]) => {
      const result = (await bridge.callApi(apiName, args)) as {
        error: any;
        data: any;
      };
      if (result.error) {
        throw result.error;
      }
      return result.data;
    };
  });
  console.log("API loaded");
})();

export default host;
