import React from "react";
import { PropsWithChildren } from "./Component";
import { twMerge } from "tailwind-merge";

export default function Button(
  props: PropsWithChildren & {
    onClick?: () => void;
  }
) {
  return (
    <button className={twMerge("bg-primary rounded p-1", props.className)} onClick={props.onClick}>
      {props.children}
    </button>
  );
}
