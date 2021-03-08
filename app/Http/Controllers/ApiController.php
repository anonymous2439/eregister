<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use SimpleSoftwareIO\QrCode\Facades\QrCode;
use Auth;
use Session;

class ApiController extends Controller
{
    public function qrcode(Request $request, $id){
    	$image = QrCode::format('png')->size(200)->generate($id);
		return response($image)->header('Content-type','image/png');
    }
}
