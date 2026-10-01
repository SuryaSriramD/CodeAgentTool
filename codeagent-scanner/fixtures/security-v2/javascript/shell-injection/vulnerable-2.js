const child_process = require("child_process");
const fs = require("fs");
function handler(req, res) {
const command = req.body.command; child_process.exec(command);
}
