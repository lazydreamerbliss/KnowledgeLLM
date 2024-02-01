export const DefaultUserProfile = {
  foldersPath: "folders", // path to a dir that contains all profile of folders
  folders: [] as string[], // file names in foldersPath, file content is folder profile
};

export type UserProfile = typeof DefaultUserProfile;

export function GenerateFolderProfile(folderName: string, location: string) {
  return {
    name: folderName,
    location: "",
  };
}

export type FolderProfile = ReturnType<typeof GenerateFolderProfile>;
