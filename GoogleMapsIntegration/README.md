# Google Maps Integration

## Overview
Integration module that connects the Car Rental Application with Google Maps APIs to provide location-based services for rental vehicles and enhanced user experience.

## Features
- Display car locations on interactive maps
- Calculate distances between user and available cars
- Provide driving directions to car pickup locations
- Geolocation filtering for car searches
- Interactive map-based car selection

## Technologies
- Google Maps JavaScript API
- Google Maps Distance Matrix API
- Google Maps Geocoding API
- Google Cloud Platform account
- RESTful integration services

## Integration Components
1. **API Client Library**
   - JavaScript wrapper for Google Maps APIs
   - Authentication management

2. **Location Services**
   - Car location data management
   - Geocoding and reverse geocoding

3. **Distance Calculations**
   - User-to-car distance matrix
   - Route optimization

4. **Map Visualization**
   - Interactive car location markers
   - Custom map styling for the application

## Setup Instructions
1. Create Google Cloud Platform account
2. Enable required Google Maps APIs:
   - Maps JavaScript API
   - Distance Matrix API
   - Geocoding API
   - Places API
3. Generate API keys with appropriate restrictions
4. Configure the client library with API keys

## Integration with Car Rental Backend
The Google Maps Integration connects with the backend via:
1. REST endpoints for car location data
2. Location-aware search filtering
3. Distance-based car recommendations

## Implementation Steps
1. Set up Google Maps API keys and credentials
2. Create map visualization components
3. Implement geocoding services for address handling
4. Build distance calculation services
5. Integrate with car search and filtering

## Usage Example
```javascript
// Initialize map with car locations
async function initializeMap(elementId) {
  const map = await mapsClient.createMap({
    elementId: elementId,
    center: { lat: 48.2082, lng: 16.3738 }, // Vienna
    zoom: 12
  });
  
  // Load car locations from API
  const cars = await api.getCars();
  
  // Add markers for each car
  cars.forEach(car => {
    map.addMarker({
      position: { lat: car.latitude, lng: car.longitude },
      title: `${car.name} - ${car.model}`,
      info: `$${car.pricePerDay}/day`
    });
  });
  
  return map;
}
```

## License
TBD