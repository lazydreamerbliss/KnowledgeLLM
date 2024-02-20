const tailwindConfig = {
  theme: {
    colors: {
      primary: "#1d4ed8",
      primaryActive: "#1e40af",
    },
    backgroundColor: {
      base: "#181818",
      baseActive: "#000000",
      primary: "#1d4ed8",
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

export function ApplyGlobalTheme() {
  // config tailwind css
  (window as any).tailwind.config = tailwindConfig; // this helps to apply the style after hot reload
}
