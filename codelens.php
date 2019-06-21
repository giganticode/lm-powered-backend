<?php

$days = $_REQUEST['days'] ?? 7;
$bars = $_REQUEST['bars'] ?? 4;
$subject = $_REQUEST['subject'] ?? "";

$sparkline = [];
for ($i = 0; $i < $bars; $i++) {
	$sparkline[] = random_int(0, 100);
}

echo json_encode([
	'number_of_calls' => random_int(5, 100),
	'number_of_fails' => random_int(0, 10),
	'count' => random_int(0,10),
	'history' => $sparkline
]);