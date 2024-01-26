import React from "react";

export default function UX() {
  const [test, setTest] = React.useState("");
  const [error, setError] = React.useState(false);

  return (
    <div className="w-full h-full bg-slate-400">
      <div className="w-full h-full grid place-items-center">
        <div className=" bg-slate-100 rounded-xl md:p-8 dark:bg-slate-800 shadow-lg ">
          {error ? <>Cannot connect to server!</> : test ? <>You are the {test}th visitor!</> : <>Connecting</>}
        </div>
      </div>
    </div>
  );
}
