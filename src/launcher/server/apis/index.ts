import Router from "koa-router";
import { Sleep } from "../util/common";

let visit = 0;
export async function ApiRouter(): Promise<Router> {
  const router = new Router();
  router.all("/", async (ctx, next) => {
    ctx.body = "Hello World";
    await next();
  });

  return router;
}
