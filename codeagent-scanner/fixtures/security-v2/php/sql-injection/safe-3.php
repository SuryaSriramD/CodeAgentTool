<?php
function handler($db) {
$db->query("SELECT count(*) FROM users");
}
