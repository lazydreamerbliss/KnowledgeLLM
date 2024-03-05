import React from "react";
import { useApplyGlobalTheme } from "./tailwind.config";
import TitleBar from "./modules/TitleBar";
import TextInput from "./components/TextInput";
import Button from "./components/Button";
import LibPanel from "./modules/LibPanel";
import ActivityBar from "./modules/ActivityBar";

export default function App() {
  useApplyGlobalTheme();
  return (
    <div className="w-full h-full bg-base text-base flex flex-col">
      <TitleBar />
      <div className="flex flex-1 flex-row">
        <ActivityBar />
        <LibPanel />
        <div className="flex-1 bg-workbench">
          This is workbench
          <TextInput placeholder="Place holder holder 1" />
          <Button>Cancel</Button>
          <Button primary>OK</Button>
        </div>
        <div className="p-1">This is ai panel</div>
      </div>
    </div>
  );
}
