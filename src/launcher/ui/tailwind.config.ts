import { useEffect } from "react";

export function useApplyGlobalTheme() {
  const tailwindConfig = {
    theme: {
      colors: {
        primary: "#225cff",
        primaryActive: "#1e40af",
      },
      backgroundColor: {
        base: "#181818",
        baseActive: "#000000",
        baseSelected: "#303030",
        primary: "#225cff",
        primaryActive: "#1e40af",
        workbench: "#1f1f1f",
        appBar: "#272727",
        textArea: "#3f3f3f",
      },
      borderColor: {
        base: "#8f8f8f",
      },
      textColor: {
        base: "#dfdfdf",
      },
    },
  };

  useEffect(() => {
    // config tailwind css
    (window as any).tailwind.config = tailwindConfig; // this helps to apply the style after hot reload
    console.log("tailwind config applied");
  }, []);
}
