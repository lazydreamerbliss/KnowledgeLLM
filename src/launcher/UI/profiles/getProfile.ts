import environments from "../utility/environments";
import { userDataPath } from "../utility/environments";
import Bridge from "../utility/bridge-render";
import { FsAccessMode } from "../../backend/bridge/bridgeTypes";
import Path from "path";

const profileFolderName = "KL-Launcher";
const profileFolderPath = Path.join(userDataPath, profileFolderName);

export async function getProfile() {
  try {
    await Bridge.fsAccess(profileFolderPath, FsAccessMode.F_OK);
  } catch (e) {
    console.log(e);
    console.log("userDataPath not found, creating one...");
  }
}
