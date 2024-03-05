import React from "react";

export default function useUI<TCallArg, TCallResult>(
  render: (
    props:
      | {
          callArg: TCallArg;
          resolve: (result: TCallResult) => void;
        }
      | undefined
  ) => JSX.Element
) {
  const [uiProps, setUiProps] = React.useState<{
    callArg: TCallArg;
    resolve: (result: TCallResult) => void;
  }>();
  return [
    (callArg: TCallArg) => {
      return new Promise<TCallResult>((resolve) => {
        setUiProps({ resolve, callArg });
      });
    },
    render(
      !!uiProps
        ? {
            callArg: uiProps.callArg,
            resolve: (result) => {
              uiProps.resolve(result);
              setUiProps(undefined);
            },
          }
        : undefined
    ),
  ];
}
