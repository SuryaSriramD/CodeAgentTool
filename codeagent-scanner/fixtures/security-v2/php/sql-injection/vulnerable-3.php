<?php
function handler($db) {
$order=$_REQUEST["sort"]; $db->exec("SELECT * FROM users ORDER BY ".$order);
}
