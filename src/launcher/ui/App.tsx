import React from "react";
import { tailwindConfig } from "./tailwind.config";
import TitleBar from "./modules/TitleBar";

export default function UX() {
  React.useEffect(() => {
    (window as any).tailwind.config = tailwindConfig; // this helps to apply the style after hot reload
  }, []);
  return (
    <div className="w-full h-full bg-base text-base flex flex-col">
      <TitleBar />
      <div className="flex flex-1 flex-row">
        <div className="p-1">This is lib panel</div>
        <div className="flex-1 bg-workbench">This is workbench</div>
        <div className="p-1">This is ai panel</div>
      </div>
    </div>
  );
}
