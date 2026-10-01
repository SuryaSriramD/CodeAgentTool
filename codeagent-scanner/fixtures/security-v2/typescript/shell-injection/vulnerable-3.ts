const child_process = require("child_process");
const fs = require("fs");
function handler(req, res) {
let file = req.params.file; child_process.exec("cat " + file);
}
