import { Environments } from "../../backend/bridge/bridgeTypes";

export default (window as any).environments as Environments;

export const userDataPath = (window as any).userDataPath as string;
