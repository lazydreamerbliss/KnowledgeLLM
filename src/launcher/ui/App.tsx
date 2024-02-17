import React from "react";
import { jsonStringify } from "./utility/common";
import { tailwindConfig } from "./tailwind.config";

export default function UX() {
  React.useEffect(() => {
    (window as any).tailwind.config = tailwindConfig;
  }, []);
  const [content, setContent] = React.useState("");
  return (
    <div className="w-full h-full bg-base text-base">
      <div className="w-full h-full grid place-items-center">
        <div
          className=" bg-primary rounded-xl md:p-8 dark:bg-slate-800 shadow-lg "
          onClick={async () => {
            jsonStringify({ a: 1 });
          }}
        >
          Open Folder
        </div>
        <input
          type="text"
          placeholder="Input title"
          value={content}
          onChange={async (e) => {
            setContent(e.target.value);
          }}
        />
        <input type="text" placeholder="Input title" />
      </div>
    </div>
  );
}
