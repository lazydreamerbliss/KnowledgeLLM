const path = require("path");
const nodeExternals = require("webpack-node-externals");

function getConfig(fileName) {
  return {
    entry: path.resolve(__dirname, `${fileName}.ts`),
    output: {
      filename: `${fileName}.js`,
      path: path.resolve(__dirname, "dist"),
    },
    node: {
      __dirname: false,
    },
    resolve: {
      extensions: [".ts", ".js"],
    },
    mode: "development",
    devtool: "inline-source-map",
  };
}

module.exports = [
  {
    ...getConfig("main"),
    target: "electron-main",
    externals: [nodeExternals(), "electron", "electron/main"],
  },
  {
    ...getConfig("preload"),
    target: "node",
  },
  {
    ...getConfig("server"),
    target: "node",
    externals: [nodeExternals()],
  },
];
