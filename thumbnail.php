<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
ini_set("error_log", "phperrors.txt");
error_log( "Hello, errors!" );

function myLog($message) {
	$now = new DateTime();
	file_put_contents("tlog.txt", $now->format('Y-m-d H:i:s.u')." -> $message \n", FILE_APPEND | LOCK_EX);
}

function calculateTextBox($text,$fontFile,$fontSize,$fontAngle) { 
    /************ 
    simple function that calculates the *exact* bounding box (single pixel precision). 
    The function returns an associative array with these keys: 
    left, top:  coordinates you will pass to imagettftext 
    width, height: dimension of the image you have to create 
    *************/ 
    $rect = imagettfbbox($fontSize,$fontAngle,$fontFile,$text); 
    $minX = min(array($rect[0],$rect[2],$rect[4],$rect[6])); 
    $maxX = max(array($rect[0],$rect[2],$rect[4],$rect[6])); 
    $minY = min(array($rect[1],$rect[3],$rect[5],$rect[7])); 
    $maxY = max(array($rect[1],$rect[3],$rect[5],$rect[7])); 
    
    return array( 
     "left"   => abs($minX) - 1, 
     "top"    => abs($minY) - 1, 
     "width"  => $maxX - $minX, 
     "height" => $maxY - $minY, 
     "box"    => $rect 
    ); 
} 

$cwd = getcwd();
$font_file = "$cwd\\consola.ttf";
$post = json_decode(file_get_contents('php://input'), true);

$width = $post['width'] ?? 325;
$text = $post['input'] ?? "";
$text = str_replace("\t", "    ", $text);;
$size = calculateTextBox($text, $font_file, 5, 0);
$height = $size['height'] + 8;

// Erzeuge das Bild
$im = imagecreate($width, $height);

$black = imagecolorallocate($im, 156, 220, 254);
$white = imagecolorallocate($im, 0, 0, 0);
imagecolortransparent($im, $black);

// Füge den Text hinzu
imagettftext($im, 5, 0, 5, 8, $white, $font_file, $text);

// Die Verwendung von imagepng() ergibt bessere Textqualität als imagejpeg()
header('Content-Type: image/png');

imagepng($im);
imagedestroy($im);
