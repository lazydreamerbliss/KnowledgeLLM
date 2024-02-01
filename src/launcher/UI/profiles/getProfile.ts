import environments from "../utility/environments";
import { userDataPath } from "../utility/environments";
import Bridge from "../utility/bridge-render";
import Path from "path";
import { GetDefaultUserProfile, UserProfile } from "./profile.json";
import { FsAccessMode, FsOpenMode } from "../../backend/bridge/bridgeTypes";
import { jsonStringify } from "../utility/common";

const profileFolderName = "KL-Launcher";
const profileFolderPath = Path.join(userDataPath, profileFolderName);
const userProfileFileName = "userProfile.json";
const userProfileFilePath = Path.join(profileFolderPath, userProfileFileName);

export async function getProfile() {
  const userProfile = await getUserProfile();
  const profileWithUserInfo = {
    id: userProfile.id,
  };
  const folderProfilesPath = Path.join(profileFolderPath, userProfile.folderProfilesLocation);
  const folderProfiles = await getFoldersProfiles(folderProfilesPath, userProfile.folders);
  const finalProfile = {
    ...profileWithUserInfo,
    folderProfiles,
  };
  return finalProfile;
}

async function getUserProfile() {
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
      console.log("User profile file not found", reason);
      return false;
    });

  if (!existUserProfile) {
    console.log("Auto creating user profile file");
    await Bridge.fsWriteFile(userProfileFilePath, jsonStringify(GetDefaultUserProfile()), FsOpenMode.ax);
  }

  return JSON.parse(await Bridge.fsReadFile(userProfileFilePath)) as UserProfile;
}

type FolderProfile =
  | {
      name: string;
      id: string;
      location: string;
    }
  | {
      errorMessage: string;
    };

async function getFoldersProfiles(
  folderProfilesLocation: string,
  foldersProfileFiles: string[]
): Promise<FolderProfile[]> {
  const existProfileFolder = await Bridge.fsAccess(folderProfilesLocation, FsAccessMode.F_OK)
    .then(() => true)
    .catch((reason) => {
      console.log("Profile folder not found", reason);
      return false;
    });

  if (!existProfileFolder) {
    return foldersProfileFiles.map((folderProfileFile) => ({
      errorMessage: `Folder profile file ${folderProfileFile} not exit`,
    }));
  }

  return await Promise.all(
    foldersProfileFiles.map(async (folderProfileFile) => {
      const folderProfileFilePath = Path.join(folderProfilesLocation, folderProfileFile);
      const existFolderProfileFile = await Bridge.fsAccess(folderProfileFilePath, FsAccessMode.F_OK)
        .then(() => true)
        .catch((reason) => {
          console.log("Folder profile file not found", reason);
          return false;
        });

      if (!existFolderProfileFile) {
        return {
          errorMessage: `Folder profile file ${folderProfileFile} not exit`,
        };
      }

      return JSON.parse(await Bridge.fsReadFile(folderProfileFile)) as FolderProfile;
    })
  );
}
