from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Trip
from .serializers import TripSerializer
from .mapbox_utils import get_route_directions 
from .hos_calculator import calculate_trip_logs 
from datetime import datetime 

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all().order_by('-created_at')
    serializer_class = TripSerializer

    def perform_create(self, serializer):
    
        trip = serializer.save()

        print(f"DEBUG VIEWS: Trip pickup_location: {trip.pickup_location}")
        print(f"DEBUG VIEWS: Trip dropoff_location: {trip.dropoff_location}") 

    
        route_info = get_route_directions(trip.pickup_location, trip.dropoff_location)

        if route_info:
            
            trip.route_distance_miles = route_info['distance_miles']
            trip.route_duration_hours = route_info['duration_hours']
            trip.route_geojson = route_info['route_geojson']


            trip_start_time = datetime.utcnow() 

            hos_results = calculate_trip_logs(
                start_time=trip_start_time,
                total_driving_hours=float(trip.route_duration_hours), 
                total_distance_miles=float(trip.route_distance_miles),
                initial_cycle_used_hours=float(trip.current_cycle_used_hrs)
            )

            if hos_results:
               
                trip.daily_logs = hos_results['daily_logs']
                trip.stops = hos_results['stops']
             


            trip.save() 
        else:
            print(f"Warning: Could not get route directions for Trip ID {trip.id}. HOS calculation skipped.")
            
            