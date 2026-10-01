const child_process = require("child_process");
const fs = require("fs");
function handler(req, res) {
const allowed = {logo:"/srv/logo.png"}; fs.readFileSync(allowed.logo);
}
