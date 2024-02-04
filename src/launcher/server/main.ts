import Koa from "koa";
import Cors from "koa-cors";
import Logger from "koa-logger";
import { ApiRouter } from "./apis";

(async function StartServer() {
  const app = new Koa();

  app.use(Cors());

  app.use(Logger());

  const router = await ApiRouter();
  app.use(router.routes());
  app.use(router.allowedMethods());

  app.listen(5011);
})();
