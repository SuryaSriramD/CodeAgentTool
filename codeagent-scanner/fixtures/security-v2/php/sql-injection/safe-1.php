<?php
function handler($db) {
$stmt=$db->prepare("SELECT * FROM users WHERE name=?"); $stmt->execute([$_GET["name"]]);
}
