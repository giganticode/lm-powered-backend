<?php

$post = json_decode(file_get_contents('php://input'), true);

$input = $post['input'] ?? "";

$lines = preg_split("/\r\n|\n|\r/", $input);

$ret = [];

foreach($lines as $line) {
	$ret[] = strlen($line) < 60;
}

echo json_encode($ret);
