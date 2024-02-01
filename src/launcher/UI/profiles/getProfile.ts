import environments from "../utility/environments";
import { userDataPath } from "../utility/environments";
import Bridge from "../utility/bridge-render";
import { FsAccessMode } from "../../backend/bridge/bridgeTypes";
import Path from "path";

const profileFolderName = "KL-Launcher";
const profileFolderPath = Path.join(userDataPath, profileFolderName);
const userProfileFileName = "userProfile.json";

export async function getProfile() {
  const existProfileFolder = await Bridge.fsAccess(profileFolderPath, FsAccessMode.F_OK)
    .then(() => true)
    .catch((reason) => {
      console.error("Profile folder not found", reason);
      return false;
    });

  if (!existProfileFolder) {
    console.log("Profile folder not found, creating...");
    await Bridge.fsMkdir(profileFolderPath);
  }
}
