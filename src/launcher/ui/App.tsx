import React from "react";
import { tailwindConfig } from "./tailwind.config";
import TextInput from "./components/TextInput";
import Button from "./components/Button";
import { getTitleBarRect } from "./util/runtimeHelper";
import Label from "./components/Lable";
import { getAppSettings } from "./api";

export default function UX() {
  const [titleBarRect, setTitleBarRect] = React.useState(getTitleBarRect);
  React.useLayoutEffect(() => {
    (window as any).tailwind.config = tailwindConfig; // this helps to apply the style after hot reload
    function updateSize() {
      const titleBarRect = getTitleBarRect();
      setTitleBarRect(titleBarRect);
      console.log("resized: ", titleBarRect);
    }
    window.addEventListener("resize", updateSize);
    updateSize();
    return () => window.removeEventListener("resize", updateSize);
  }, []);
  return (
    <div className="w-full h-full bg-base text-base flex flex-col">
      <header
        className="app-drag px-1 bg-appBar flex flex-row text-xs justify-between items-center"
        style={{
          height: titleBarRect.height, // this make sure the title bar is the same height as the control overlay
          width: titleBarRect.width, // this avoids rendering contents behind control overlay
        }}
      >
        <Label>Hello!</Label>
        <TextInput className="py-0" placeholder="Search" />
        <Button
          className="py-0"
          onClick={async () => {
            console.log(await getAppSettings());
          }}
        >
          Button
        </Button>
      </header>
      <div className="flex flex-1 flex-row">
        <div className="p-1">This is lib panel</div>
        <div className="flex-1 bg-workbench">This is workbench</div>
        <div className="p-1">This is ai panel</div>
      </div>
    </div>
  );
}
