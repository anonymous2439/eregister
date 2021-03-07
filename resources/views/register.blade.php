@extends('layouts.base')

@section('head')
	<script type="text/javascript" src="lib/instascan/instascan3.min.js"></script>
@endsection

@section('body')
	<div class="container">
		Register
		@isset($messages)
			@if(count($messages['success'])>0)
				@foreach($messages['success'] as $s)
					<div class="alert alert-success alert-dismissible fade show" role="alert" style="margin-top:15px;">
					  <strong>{{ $s }}</strong>.
					  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
					</div>
				@endforeach
			@endif
		@endisset
		<form action="/user" method="post">
			@csrf
			<label>First Name <input id="fname" name="fname" class="form-control" required></label>
			<label>Last Name <input id="lname" name="lname" class="form-control" required></label>
			<label>Phone Number <input id="phone" name="phone" class="form-control" required></label>
			<label>E-mail <input type="email" id="email" name="email" class="form-control" required></label>
			<label>Course <input id="course" name="course" class="form-control" required></label>
			<label>Password <input id="password" type="password" name="password" class="form-control" required></label>
			<label>Confirm password <input id="password2" type="password" name="password2" class="form-control" required></label>
			<label>Year<input id="year" name="year" class="form-control" required></label>
			<input type="hidden" value="2" name="role">
			<div class="d-flex justify-content-end">
				<button type="submit" class="btn btn-primary">Submit</button>
			</div>
		</form>

		<div>
		    <video id="preview"></video>
		    <script type="text/javascript">
		      let scanner = new Instascan.Scanner({ video: document.getElementById('preview') });
		      scanner.addListener('scan', function (content) {
		      	alert(content);
		        //console.log(content);
		      });
		      Instascan.Camera.getCameras().then(function (cameras) {
		        if (cameras.length > 0) {
		          scanner.start(cameras[1]);
		        } else {
		          console.error('No cameras found.');
		        }
		      }).catch(function (e) {
		        console.error(e);
		      });
		    </script>
		</div>
	</div>
@endsection