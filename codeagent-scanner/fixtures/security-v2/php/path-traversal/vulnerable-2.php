<?php
function handler($db) {
$path="/srv/".$_POST["file"]; file_get_contents($path);
}
