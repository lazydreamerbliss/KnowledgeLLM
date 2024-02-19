import React from "react";
import { getTitleBarRect, platform, windowEvents } from "../util/runtimeHelper";
import TextInput from "../components/TextInput";
import Button from "../components/Button";
import Label from "../components/Label";
import { getAppSettings } from "../api";

export default function TitleBar() {
  const [titleBarRect, setTitleBarRect] = React.useState(getTitleBarRect);
  const [isFullScreen, setIsFullScreen] = React.useState(false);
  const isMac = platform === "darwin";
  React.useEffect(() => {
    const updateSize = () => {
      const titleBarRect = getTitleBarRect();
      setTitleBarRect(titleBarRect);
      console.log("resized: ", titleBarRect);
    };
    const handelEnterEnterFullScreen = () => setIsFullScreen(true);
    const handelLeaveFullScreen = () => setIsFullScreen(false);

    windowEvents.sizeChanged.on(updateSize);
    windowEvents.enterFullScreen.on(handelEnterEnterFullScreen);
    windowEvents.leaveFullScreen.on(handelLeaveFullScreen);
    return () => {
      windowEvents.sizeChanged.removeEventListener(updateSize);
      windowEvents.enterFullScreen.removeEventListener(handelEnterEnterFullScreen);
      windowEvents.leaveFullScreen.removeEventListener(handelLeaveFullScreen);
    };
  }, []);

  const height = titleBarRect.height;
  const width = isFullScreen ? "100%" : titleBarRect.width;

  return (
    <header
      className="app-drag px-1 bg-appBar flex flex-row text-xs justify-between items-center"
      style={{
        height, // this make sure the title bar is the same height as the control overlay
        width, // this avoids rendering contents behind control overlay
        ...(isMac && { float: "right" }),
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
