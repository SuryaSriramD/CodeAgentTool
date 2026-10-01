const child_process = require("child_process");
const fs = require("fs");
function handler(req, res) {
const path = "/srv/" + req.body.file; fs.readFileSync(path);
}
