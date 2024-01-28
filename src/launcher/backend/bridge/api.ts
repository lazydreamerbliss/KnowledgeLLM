/*
 * Attention !!
 * Since the type of Api will be imported by UI,
 * and UI is run in browser and cannot recognize the type of electron and nodejs,
 * so we had better to convert to the simple type and mark the type before return.
 * So that UI can recognize the type.
 */

export default function Api() {
  return {
    log: (message: string) => {
      console.log(message);
    },
    pickFolder: async () => {
      const { dialog } = require("electron");
      const result = await dialog.showOpenDialog({
        properties: ["openDirectory"],
      });
      return {
        canceled: result.canceled as boolean,
        filePaths: result.filePaths as string[],
      };
    },
  };
}

export type TypeApi = ReturnType<typeof Api>;
