<?php
function handler($db) {
mysqli_query($db,"SELECT * FROM users");
}
