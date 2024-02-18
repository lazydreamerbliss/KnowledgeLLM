import Router from "koa-router";
import { AppSettings } from "../../common/apiDataContract";

export function BuildSettingApis(router: Router) {
  router.get("/settings", async (ctx, next) => {
    const settings: AppSettings = {
      testSettingContent: "This is a test setting content",
    };
    ctx.body = settings;
  });
}
