@extends('layouts.base')

@section('body')
	<div class="container">
		@if(count($errors)>0)
			@foreach($errors as $error)
				<div class="alert alert-danger alert-dismissible fade show" role="alert" style="margin-top:15px;">
				  <strong>{{ $error }}</strong>.
				  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
				</div>
			@endforeach
		@endif
		<div id="login-row" class="row justify-content-center align-items-center">
            <div id="login-column" class="col-md-6">
                <div id="login-box" class="col-md-12">
                    <form id="login-form" class="form" action="/login" method="post">
                    	@csrf
                        <h3 class="text-center text-info">Administrator Login</h3>
                        <div class="form-group">
                            <label for="email" class="text-info">E-mail / Phone Number:</label><br>
                            <input type="text" name="email" id="email" class="form-control">
                        </div>
                        <div class="form-group">
                            <label for="password" class="text-info">Password:</label><br>
                            <input type="password" name="password" id="password" class="form-control">
                        </div>
                        <div class="form-group">
                            <input type="submit" name="submit" class="btn btn-info btn-md" value="submit">
                        </div>
                    </form>
                </div>
            </div>
        </div>
	</div>
@endsection