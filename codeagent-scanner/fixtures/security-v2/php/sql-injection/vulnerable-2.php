<?php
function handler($db) {
$id=$_POST["id"]; $db->query("DELETE FROM users WHERE id=".$id);
}
