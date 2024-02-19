import React from "react";
import { getTitleBarRect, platform, windowEvents } from "../util/runtimeHelper";
import TextInput from "../components/TextInput";
import Button from "../components/Button";
import Label from "../components/Label";
import { getAppSettings } from "../api";

export default function TitleBar() {
  const [titleBarRect, setTitleBarRect] = React.useState(getTitleBarRect);
  const isMac = platform === "darwin";
  React.useEffect(() => {
    const updateSize = () => {
      const titleBarRect = getTitleBarRect();
      setTitleBarRect(titleBarRect);
      console.log("resized: ", titleBarRect);
    };
    window.addEventListener("resize", updateSize);

    const onMaximize = () => {
      console.log("maximized");
    };
    windowEvents.maximize.on(onMaximize);

    const onUnmaximize = () => {
      console.log("unmaximized");
    };
    windowEvents.unmaximize.on(onUnmaximize);
    updateSize();
    return () => {
      window.removeEventListener("resize", updateSize);
      windowEvents.maximize.removeEventListener(onMaximize);
      windowEvents.unmaximize.removeEventListener(onUnmaximize);
    };
  }, []);
  return (
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
  );
}
