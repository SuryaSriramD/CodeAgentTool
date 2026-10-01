<?php
function handler($db) {
$name=$_GET["name"]; mysqli_query($db,"SELECT * FROM users WHERE name=".$name);
}
