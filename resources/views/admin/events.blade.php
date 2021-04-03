@extends('layouts.base')

@section('body')
	<div class="container">
		Events
		<a href="/admin">Dashboard</a>
		<a href="/logout">Logout</a>

		<form action="/event" method="post">
			@csrf
			Create Event
			<input class="form-control" placeholder="Event name" name="event_name">
			<input class="form-control" placeholder="Venue" name="event_venue">
			<select class="form-control" name="event_type">
			@foreach($eventTypes as $type)
				<option value="{{ $type->id }}">{{ $type->name }}</option>
			@endforeach
			</select>
			<button class="btn btn-primary">Save</button>
		</form>
	</div>
@endsection