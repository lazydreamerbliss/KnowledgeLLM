import environments from "../utility/environments";
import { userDataPath } from "../utility/environments";
import Bridge from "../utility/bridge-render";
import Path from "path";
import { GetDefaultUserProfile } from "./profile.json";
import { FsAccessMode, FsOpenMode } from "../../backend/bridge/bridgeTypes";
import { jsonStringify } from "../utility/common";

const profileFolderName = "KL-Launcher";
const profileFolderPath = Path.join(userDataPath, profileFolderName);
const userProfileFileName = "userProfile.json";
const userProfileFilePath = Path.join(profileFolderPath, userProfileFileName);

export async function getProfile() {
  const existProfileFolder = await Bridge.fsAccess(profileFolderPath, FsAccessMode.F_OK)
    .then(() => true)
    .catch((reason) => {
      console.log("Profile folder not found", reason);
      return false;
    });

  if (!existProfileFolder) {
    console.log("Auto creating profile folder...");
    await Bridge.fsMkdir(profileFolderPath);
  }

  const existUserProfile = await Bridge.fsAccess(userProfileFilePath, FsAccessMode.F_OK)
    .then(() => true)
    .catch((reason) => {
      console.log("User profile not found", reason);
      return false;
    });

  if (!existUserProfile) {
    console.log("Auto creating user profile file");
    await Bridge.fsWriteFile(userProfileFilePath, jsonStringify(GetDefaultUserProfile()), FsOpenMode.ax);
  }
}
