import React, { useState } from "react";
import { PropsWithChildren } from "./Component";
import { twMerge } from "tailwind-merge";

export default function Button(
  props: PropsWithChildren & {
    primary?: boolean;
    onClick?: () => void;
  }
) {
  return (
    <button
      className={twMerge(
        "rounded px-0.5 transform transition-transform font-medium",
        props.primary ? "bg-primary active:bg-primaryActive" : "border border-base active:bg-baseActive",
        props.className
      )}
      onClick={props.onClick}
    >
      {props.children}
    </button>
  );
}
