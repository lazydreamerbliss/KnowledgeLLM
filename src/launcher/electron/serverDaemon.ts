import { fork, ChildProcess } from "node:child_process";
import { watch } from "node:fs";

function lazy(ms: number, fn: () => void): () => void {
  let promise: Promise<void> | null = null;
  return () => {
    if (promise) {
      return promise;
    }
    promise = new Promise((resolve, reject) => {
      setTimeout(() => {
        promise = null;
        try {
          fn();
        } catch (e) {
          reject(e);
        }
      }, ms);
    });
  };
}

let server: ChildProcess;
let serverGeneration = 0;

const lazyStartServer = lazy(1000, () => {
  if (server) {
    server.kill();
  }
  console.log("starting server");
  server = fork("./dist/server.js", [serverGeneration.toString()], {
    stdio: "pipe",
  });
  serverGeneration++;
  server.on("exit", (code) => {
    console.log(`server exited with code ${code}`);
  });
});

export function startServer() {
  watch("./dist/server.js", (name) => {
    console.log("server.js action: ", name);
    lazyStartServer();
  });
  lazyStartServer();
}
