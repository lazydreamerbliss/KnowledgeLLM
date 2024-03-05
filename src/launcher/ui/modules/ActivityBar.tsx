import React from "react";
import { DriveIcon } from "../components/icons/ActivityBarIcons";
import { twMerge } from "tailwind-merge";

export default function ActivityBar() {
  return (
    <div className="border-r border-base/25">
      <ActivityBarItem icon={DriveIcon} description="Drives" active />
      <ActivityBarItem icon={DriveIcon} description="Drives" active={false} />
    </div>
  );
}

function ActivityBarItem(props: { icon: JSX.Element; description: string; active: boolean }) {
  return (
    <button
      className={twMerge(
        "m-1 p-2 text-center items-center w-10 h-10 rounded-xl border-none hover:bg-primary block",
        props.active ? "bg-baseSelected" : ""
      )}
      aria-label={props.description}
    >
      {DriveIcon}
    </button>
  );
}
