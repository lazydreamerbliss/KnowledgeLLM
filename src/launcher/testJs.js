const fs = require("node:fs/promises");

(async () => {
  const data = await fs.access("./testJdds.js", 0);
  console.log(data);
})();
