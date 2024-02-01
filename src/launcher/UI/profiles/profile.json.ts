import { randomUUID } from "../utility/common";

export function GetDefaultUserProfile() {
  return {
    foldersPath: "folders", // path to a dir that contains all profile of folders
    folders: [] as string[], // file names in foldersPath, file content is folder profile
  };
}

export type UserProfile = ReturnType<typeof GetDefaultUserProfile>;

export function GenerateFolderProfile(folderName: string) {
  return {
    name: folderName,
    id: randomUUID(),
    location: "",
  };
}

export type FolderProfile = ReturnType<typeof GenerateFolderProfile>;
