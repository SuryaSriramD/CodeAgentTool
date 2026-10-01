const child_process = require("child_process");
const fs = require("fs");
function handler(req, res) {
fs.readFile(req.query.path, () => {});
}
