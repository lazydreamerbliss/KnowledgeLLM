const path = require("path");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const ReactRefreshPlugin = require("@pmmmwh/react-refresh-webpack-plugin");
const nodeExternals = require("webpack-node-externals");

const isServe = !!process.env.WEBPACK_SERVE;

const configForWeb = {
  name: "web",
  entry: {
    index: __dirname + "/ui/index.ts",
  },
  output: {
    filename: "bundle.js",
    path: path.resolve(__dirname, "dist"),
  },
  plugins: [
    new CopyWebpackPlugin({ patterns: [__dirname + "/ui/static"] }),
    ...(isServe ? [new ReactRefreshPlugin()] : []),
  ],
  devServer: {
    port: 5012,
    static: __dirname + "/ui/static",
    hot: true,
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        loader: "babel-loader",
        options: {
          plugins: [require.resolve("react-refresh/babel")],
          configFile: __dirname + "/ui/.babelrc",
        },
      },
      {
        test: /\.tsx?$/,
        exclude: /node_modules/,
        use: [
          {
            loader: "ts-loader",
            options: {
              onlyCompileBundledFiles: true,
            },
          },
        ],
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
  },
};

const configForServer = {
  name: "server",
  entry: path.resolve(__dirname, "server", "main"),
  output: {
    filename: "server.js",
    path: path.resolve(__dirname, "dist"),
  },
  target: "node",
  externals: [nodeExternals()],
  node: {
    __dirname: false,
  },
  module: {
    rules: [
      {
        test: /\.ts/,
        use: [
          {
            loader: "ts-loader",
            options: {
              onlyCompileBundledFiles: true,
            },
          },
        ],
        exclude: /node_modules/,
      },
    ],
  },
  resolve: {
    extensions: [".ts", ".js"],
  },
  devServer: {
    devMiddleware: {
      writeToDisk: true,
    },
  },
};

module.exports = [configForWeb, configForServer];
