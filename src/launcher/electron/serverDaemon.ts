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

// let server: ChildProcess;
// let serverGeneration = 0;

let server:
  | {
      process: ChildProcess;
      generation: number;
    }
  | undefined;

const lazyStartServer = lazy(1000, () => {
  let serverGeneration = 0;
  if (server !== undefined) {
    server.process.kill();
    serverGeneration = server.generation + 1;
  }

  console.log("Restart server");

  server = {
    process: fork("./dist/server.js", [serverGeneration.toString()], {
      stdio: "pipe",
    }),
    generation: serverGeneration,
  };
});

export function startServer() {
  watch("./dist/server.js", (name) => {
    console.log("server.js action: ", name);
    lazyStartServer();
  });
  lazyStartServer();
}
