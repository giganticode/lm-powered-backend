<?php
/*
$post = json_decode(file_get_contents('php://input'), true);

$input = $post['input'] ?? "";

$lines = preg_split("/\r\n|\n|\r/", $input);

$ret = [];

foreach($lines as $line) {
    $l = trim($line);

	if (strlen($l) == 0 || strpos($l, "//") === 0) {
        $ret[] = -1;
    } else {
        $ret[] = random_int(0,100);
	}
}

echo json_encode($ret);

/*


<?php
*/
//$now = md5(microtime(true));

function myLog($message) {
	$now = new DateTime();
	file_put_contents("log.txt", $now->format('Y-m-d H:i:s.u')." -> $message \n", FILE_APPEND | LOCK_EX);
}

function outputData($fileContent) {
	$lines = preg_split("/(\r\n|\n|\r)/", trim($fileContent));
	$values = array_map('transformEntropy', $lines);
	echo json_encode($values);
}

function transformEntropy($val) {
	$val = floatval($val);
	$val = min($val / 7.5 * 100, 100);
	return $val;
}

$supported = ['.java'];


$cwd = getcwd();
$noReturn = isset($_REQUEST['noReturn']) ? $_REQUEST['noReturn'] : false;

$post = json_decode(file_get_contents('php://input'), true);
$path = $_REQUEST['fileName'];
$filename = basename($_REQUEST['fileName']);
$aggregator = isset($_REQUEST['aggregator']) ? $_REQUEST['aggregator'] : 'full-token-average';

myLog("Endpoint called " . $filename . " -> " . $aggregator);

if (!file_exists("./output/$aggregator")) {
	mkdir("./output/$aggregator", 0755, true);
}

$languageId = isset($_REQUEST['languageId']) ? strtolower($_REQUEST['languageId']) : "";
$extension = strtolower($_REQUEST['extension']);

if (!in_array($extension, $supported)) {
	// Language is not supported.
	myLog("extension $extension not supported");
	http_response_code(406 );
	return;
}

$hash = md5($path);

$input = $post['input'] ?? "";

// check if file already exists and if they are equal -> performance
if (file_exists("./tmp/$hash") && file_exists("./output/$aggregator/$hash")){
	$cachedContent = file_get_contents("./tmp/$hash");
	myLog("  file is cached");
	
	if ($cachedContent == $input) {
		myLog("  file has not been modified and can be returned");
		$o = file_get_contents("./output/$aggregator/$hash");
		outputData($o);
		return;
	}
	
}

file_put_contents("./tmp/$hash", $input);

// aggregator function -e: subtoken-average, full-token-average default, full-token-entropies

$command = escapeshellcmd("python ./langmodels/langmodels/inference/entropies.py ./tmp/$hash -o \"./output/$aggregator/$hash\" -e \"$aggregator\"");
myLog($command);
$output = shell_exec($command);

if ($noReturn) {
	return;
}

//read file and return lines
$o = file_get_contents("./output/$aggregator/$hash");

// transform input
/*$lines = preg_split("/(\r\n|\n|\r)/",$o);
$return = [];
foreach ($lines as $line) {
	$risk = floatval($line);
	$return[] = ($risk == 0) ? -1 : $risk / 7.5 * 100;
}*/

//$lines = preg_split("/(\r\n|\n|\r)/",$o);
//echo trim(json_encode($return));
outputData($o);
/*
*/
