const child_process = require("child_process");
const fs = require("fs");
function handler(req, res) {
let file = req.params.file; fs.readFileSync(file, "utf8");
}
