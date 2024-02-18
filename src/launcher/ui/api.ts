import axios from "axios";

const ax = axios.create({
  baseURL: "http://localhost:5011",
  timeout: 1000,
});

// region app setting
export async function getAppSettings() {
  return (await ax.get("/settings")).data;
}

// region library
// todo: add library apis
