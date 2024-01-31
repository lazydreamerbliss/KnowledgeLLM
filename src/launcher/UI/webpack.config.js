const path = require("path");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const ReactRefreshPlugin = require("@pmmmwh/react-refresh-webpack-plugin");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");
// const NodePolyfillPlugin = require("node-polyfill-webpack-plugin");

module.exports = function (env, args) {
  let config = {
    entry: {
      index: "./UI/index.ts",
    },
    output: {
      filename: "bundle.js",
      path: path.resolve(__dirname, "build"),
    },
    plugins: [
      new CleanWebpackPlugin(),
      new CopyWebpackPlugin({ patterns: ["UI/static"] }),
      new ReactRefreshPlugin(),
      // new NodePolyfillPlugin(),
    ],
    devServer: {
      port: 5012,
    },
    module: {
      rules: [
        {
          test: /\.(js|jsx)$/,
          exclude: /node_modules/,
          loader: "babel-loader",
          options: {
            plugins: [require.resolve("react-refresh/babel")],
            configFile: "./UI/.babelrc",
          },
        },
        {
          test: /\.tsx?$/,
          exclude: /node_modules/,
          loader: "ts-loader",
        },
        {
          test: /\.(png|jpg|gif|ttf|eot|woff|woff2)$/i,
          use: [
            {
              loader: "url-loader",
              options: { limit: 8192 },
            },
          ],
        },
      ],
    },
    resolve: {
      extensions: [".js", ".jsx", ".ts", ".tsx"],
      fallback: {
        path: require.resolve("path-browserify"),
      },
    },
  };
  if (env.WEBPACK_SERVE) {
    console.log("Gen config for development");
    config.mode = "development";
    config.devtool = "inline-source-map";
  } else {
    console.log("Gen config for production");
    config.mode = "production";
  }

  return config;
};
