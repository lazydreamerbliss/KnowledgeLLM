import React from "react";
import { jsonStringify } from "./utility/common";

export default function UX() {
  const [title, setTitle] = React.useState("UX");
  React.useEffect(() => {
    document.title = title;
    jsonStringify({ title });
  }, [title]);

  return (
    <div className="w-full h-full bg-slate-400">
      <div className="w-full h-full grid place-items-center">
        <div className=" bg-slate-100 rounded-xl md:p-8 dark:bg-slate-800 shadow-lg " onClick={async () => {}}>
          Open Folder
        </div>
        <input
          type="text"
          onChange={async (e) => {
            setTitle(e.target.value);
          }}
          value={title}
          placeholder="Input title"
        />
      </div>
    </div>
  );
}
