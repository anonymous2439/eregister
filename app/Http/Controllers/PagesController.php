<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use SimpleSoftwareIO\QrCode\Facades\QrCode;
use Auth;
use Session;

class PagesController extends Controller
{
    public function index(Request $request){
    	return view('index');
    }

    public function qrcode(Request $request, $id){
    	$image = QrCode::format('png')->size(200)->generate($id);
		return response($image)->header('Content-type','image/png');
    }

    public function register(Request $request){
    	$messages = Session::get('messages');
    	return view('register')->with(['messages' => $messages]);
    }

    public function registerSubmit(Request $request, $success){
    	return view('register')->with(['success'=>['Your have been successfully registered!']]);
    }

    public function adminIndex(Request $request){
    	if(Auth::guest()){
    		return redirect('/admin/login');
    	}
    	return view('admin.index');
    }

    public function adminLogin(Request $request){
    	return view('admin.login');
    }

    public function attemptLogin(Request $request){
    	//check if the inputted account is email
    	$user = array(
           'email'=> $request->get('email'),
           'password'=> $request->get('password')
        );
        //check if the inputted account is email
        if(Auth::attempt($user)){
        	if(Auth::user()->role->id==1)
            	return redirect('/admin');
            else
            	return redirect('/profile/'.Auth::user()->id);
        }
        //check if the inputted account is phone number
        else{
			$user = array(
	           'phone'=> $request->get('email'),
	           'password'=> $request->get('password')
	        );
	        if(Auth::attempt($user)){
	        	if(Auth::user()->role->id==1)
	            	return redirect('/admin');
	            else
	            	return redirect('/profile/'.Auth::user()->id);
	        }
        }
        
        return redirect('/admin/login')->with(['errors'=>['Incorrect E-mail / Phone Number / Password']]);
        
    }

    public function logout(Request $request){
    	Auth::logout();
    	return redirect('/');
    }

    public function profile(Request $request, $id){
    	return view('profile')->with(['id'=>$id]);
    }
}
