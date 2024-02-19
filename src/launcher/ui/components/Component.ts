import React from "react";

export type BaseProps = {
  className?: string;
};

export type PropsWithChildren = BaseProps & {
  children?: React.ReactNode;
};
