<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\PagesController;
use App\Http\Controllers\UsersController;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| contains the "web" middleware group. Now create something great!
|
*/


Route::get('/', [PagesController::class, 'index']);
Route::get('/qrcode/{id}', [PagesController::class, 'qrcode']);
Route::get('/register', [PagesController::class, 'register']);
Route::resource('/user', UsersController::class);
Route::get('/profile/{id}', [PagesController::class, 'profile']);
Route::post('/register/submit', [PagesController::class, 'registerSubmit']);
//admin
Route::get('/admin', [PagesController::class, 'adminIndex']);
Route::get('/admin/login', [PagesController::class, 'adminLogin']);
Route::post('/login', [PagesController::class, 'attemptLogin']);
Route::get('/logout', [PagesController::class, 'logout']);