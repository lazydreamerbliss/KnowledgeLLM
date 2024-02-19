import Router from "koa-router";
import { Sleep } from "../../common";
import { BuildSettingApis } from "./settings";

let visit = 0;
export function ApiRouter(): Router {
  const router = new Router();
  router.all("/", async (ctx, next) => {
    ctx.body = `Hello World! ${visit++}`;
    await Sleep(100);
  });

  BuildSettingApis(router);

  return router;
}
