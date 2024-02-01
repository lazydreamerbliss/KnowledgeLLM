import React from "react";
import Bridge from "./utility/bridge-render";
import environments from "./utility/environments";
import { getProfile } from "./profiles/getProfile";

export default function UX() {
  const [title, setTitle] = React.useState("UX");
  React.useEffect(() => {
    document.title = title;
  }, [title]);

  return (
    <div className="w-full h-full bg-slate-400">
      <div className="w-full h-full grid place-items-center">
        <div
          className=" bg-slate-100 rounded-xl md:p-8 dark:bg-slate-800 shadow-lg "
          onClick={async () => {
            // // const res = await Bridge.pickFolder();
            // // console.log(res);
            // console.log(environments);
            getProfile();
          }}
        >
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
