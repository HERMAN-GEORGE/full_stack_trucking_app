import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Polyline, Marker, useMap } from 'react-leaflet';
import { Icon } from 'leaflet';
import L from 'leaflet';
import './App.css';
import EldLogSheet from './components/EldLogSheet';

const API_BASE_URL = 'https://full-stack-trucking-app.onrender.com';

const customIcon = new Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

function MapViewUpdater({ polylinePositions }) {
  const map = useMap();

  useEffect(() => {
    if (polylinePositions.length > 1) {
      const bounds = polylinePositions.reduce((acc, pos) => acc.extend(pos), new L.LatLngBounds(polylinePositions[0], polylinePositions[0]));
      map.fitBounds(bounds, { padding: [50, 50] });
    } else if (polylinePositions.length === 1) {
      map.setView(polylinePositions[0], 10);
    }
    map.invalidateSize();
  }, [map, polylinePositions]);

  return null;
}


function App() {
  const [formData, setFormData] = useState({
    current_location: '',
    pickup_location: '',
    dropoff_location: '',
    current_cycle_used_hrs: '',
  });

  const [message, setMessage] = useState('');
  const [trips, setTrips] = useState([]);
  const [selectedTrip, setSelectedTrip] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('Submitting trip...');

    const dataToSend = {
      ...formData,
      current_cycle_used_hrs: parseFloat(formData.current_cycle_used_hrs),
    };

    try {
      const response = await axios.post(`${API_BASE_URL}/api/trips/`, dataToSend);
      setMessage('Trip created successfully!');
      console.log('Trip created:', response.data);

      setFormData({
        current_location: '',
        pickup_location: '',
        dropoff_location: '',
        current_cycle_used_hrs: '',
      });

      fetchTrips();
      setSelectedTrip(response.data);
    } catch (error) {
      setMessage(`Error creating trip: ${error.message}. Check console for details.`);
      console.error('Error creating trip:', error.response ? error.response.data : error);
    }
  };

  const fetchTrips = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/trips/`);
      setTrips(response.data);
    } catch (error) {
      console.error('Error fetching trips:', error);
    }
  };

  const handleTripSelect = async (tripId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/trips/${tripId}/`);
      setSelectedTrip(response.data);
      setMessage(`Viewing Trip ID: ${tripId}`);
    } catch (error) {
      setMessage(`Error fetching details for Trip ID ${tripId}: ${error.message}`);
      console.error('Error fetching trip details:', error);
    }
  };

  useEffect(() => {
    fetchTrips();
  }, []);

  let mapCenter = [39.8283, -98.5795];
  let polylinePositions = [];
  let pickupCoords = null;
  let dropoffCoords = null;

  if (selectedTrip && selectedTrip.route_geojson && selectedTrip.route_geojson.coordinates) {
    polylinePositions = selectedTrip.route_geojson.coordinates.map(coord => [coord[1], coord[0]]);

    if (polylinePositions.length > 0) {
      mapCenter = polylinePositions[Math.floor(polylinePositions.length / 2)];
      pickupCoords = polylinePositions[0];
      dropoffCoords = polylinePositions[polylinePositions.length - 1];
    }
  }

  return (
    <div className="App">
      <main>
        <h1>George herman moshi Trucking Trip Planner</h1>

        <div className="content-wrapper">
          <div className="left-panel">
            <h2>Enter Trip Details</h2>
            <form onSubmit={handleSubmit} className="trip-form">
              <div className="form-group">
                <label htmlFor="current_location">Current Location:</label>
                <input
                  type="text"
                  id="current_location"
                  name="current_location"
                  value={formData.current_location}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="pickup_location">Pickup Location:</label>
                <input
                  type="text"
                  id="pickup_location"
                  name="pickup_location"
                  value={formData.pickup_location}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="dropoff_location">Dropoff Location:</label>
                <input
                  type="text"
                  id="dropoff_location"
                  name="dropoff_location"
                  value={formData.dropoff_location}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="current_cycle_used_hrs">Current Cycle Used (Hrs):</label>
                <input
                  type="number"
                  id="current_cycle_used_hrs"
                  name="current_cycle_used_hrs"
                  value={formData.current_cycle_used_hrs}
                  onChange={handleChange}
                  step="0.01"
                  required
                />
              </div>

              <button type="submit">Submit Trip</button>
            </form>

            {message && <p className="message">{message}</p>}
          </div>

          <div className="right-panel">
            <h4>Route Map</h4>
            {selectedTrip && selectedTrip.route_geojson && selectedTrip.route_geojson.coordinates && polylinePositions.length > 1 ? (
              <MapContainer
                key={selectedTrip.id}
                center={mapCenter}
                zoom={5}
                scrollWheelZoom={true}
                style={{ height: '400px', width: '100%', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <MapViewUpdater polylinePositions={polylinePositions} />

                <Polyline positions={polylinePositions} color="blue" weight={5} />
                {pickupCoords && <Marker position={pickupCoords} icon={customIcon} />}
                {dropoffCoords && <Marker position={dropoffCoords} icon={customIcon} />}
              </MapContainer>
            ) : (
              <p>Submit a trip or select an existing trip to view its route map.</p>
            )}
          </div>
        </div>

        <h2>Existing Trips</h2>
        {!Array.isArray(trips) || trips.length === 0 ? (
          <p>No trips recorded yet. Submit a new trip to see it here!</p>
        ) : (
          <ul className="trip-list">
            {trips.map(trip => (
              <li key={trip.id}>
                <strong>ID:</strong> {trip.id}
                <button onClick={() => handleTripSelect(trip.id)}>View Details</button><br />
                <strong>From:</strong> {trip.pickup_location}<br />
                <strong>To:</strong> {trip.dropoff_location}<br />
                <strong>Cycle Used:</strong> {trip.current_cycle_used_hrs} hrs<br />
                <small>Created: {new Date(trip.created_at).toLocaleString()}</small>
              </li>
            ))}
          </ul>
        )}

        {selectedTrip && (
          <div className="trip-details-view">
            <h3>Details for Trip ID: {selectedTrip.id}</h3>
            <p>Distance: {selectedTrip.route_distance_miles ? parseFloat(selectedTrip.route_distance_miles).toFixed(2) + ' miles' : 'N/A'}</p>
            <p>Duration: {selectedTrip.route_duration_hours ? parseFloat(selectedTrip.route_duration_hours).toFixed(2) + ' hours' : 'N/A'}</p>

            <h4>ELD Daily Logs</h4>
            {selectedTrip.daily_logs && selectedTrip.daily_logs.length > 0 ? (
              selectedTrip.daily_logs.map((dayLog, dayIndex) => (
                <div key={dayIndex} className="daily-log-sheet-wrapper">
                  <h5>Day {dayIndex + 1} ({new Date(dayLog[0].start_time).toLocaleDateString()})</h5>
                  <EldLogSheet dailyLog={dayLog} />
                </div>
              ))
            ) : (
              <p>No ELD log data available for this trip.</p>
            )}

            <h4>Planned Stops</h4>
            {selectedTrip.stops && selectedTrip.stops.length > 0 ? (
              <ul className="stops-list">
                {selectedTrip.stops.map((stop, index) => (
                  <li key={index}>
                    <strong>{stop.type}:</strong> {new Date(stop.time).toLocaleString()} - Duration: {stop.duration_hours ? parseFloat(stop.duration_hours).toFixed(2) + ' hrs' : (parseFloat(stop.duration_minutes) / 60.0).toFixed(2) + ' hrs'} {stop.description && `(${stop.description})`}
                  </li>
                ))}
              </ul>
            ) : (
              <p>No planned stops.</p>
            )}

          </div>
        )}
      </main>
    </div>
  );
}

export default App;
