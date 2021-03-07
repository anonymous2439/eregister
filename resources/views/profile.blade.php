@extends('layouts.base')

@section('body')
	<div class="container">
		profile
	</div>
	<div>
		<img src="/qrcode/{{ $id }}">
	</div>
@endsection