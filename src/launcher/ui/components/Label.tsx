import React from "react";
import { twMerge } from "tailwind-merge";
import { PropsWithChildren } from "./Component";

export default function Label(props: PropsWithChildren) {
  return <label className={twMerge("text-base", props.className)} children={props.children} />;
}
