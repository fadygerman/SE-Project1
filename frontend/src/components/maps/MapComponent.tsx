import React, { useCallback } from 'react';
import { GoogleMap, LoadScript } from '@react-google-maps/api';
import { Car } from '@/openapi';

export interface MapComponentProps {
  center: {
    lat: number;
    lng: number;
  };
  car: Car;
}
const divStyle = {
  display: 'flex',
  justifyContent: 'center', 
  width: '100%',  
  borderradius: '8px',

};

const containerStyle = {
  width: '100%',
  height: '300px',
  borderRadius: '10px',
};



// HOW TO USE: <MapComponent center={{ lat: 48.2082, lng: 16.3738 }}></MapComponent> // optionally MapComponentProps can be enhanced

const MapComponent: React.FC<MapComponentProps> = ({ center }) => {
  const onLoad = useCallback((map: google.maps.Map) => {
    const destinationUrl = `https://www.google.com/maps/dir/?api=1&destination=${center.lat},${center.lng}`;

    const markerDiv = document.createElement('div');
    markerDiv.innerHTML = `
      <div style="
        width: 36px;
        height: 36px;
        background: #ff5722;
        border-radius: 50%;
        box-shadow: 0 0 6px rgba(0,0,0,0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 18px;
        cursor: pointer;
        padding-bottom: 5px;
      ">
        🚗
      </div>
    `;

    const marker = new google.maps.marker.AdvancedMarkerElement({
      map,
      position: center,
      content: markerDiv,
    });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (marker as any).anchor = new google.maps.Point(18, 36);


    // Add native InfoWindow
    const infoWindow = new google.maps.InfoWindow({
      content: `
        <div style="font-size:13px; min-width: 180px; text-align: center;">
          <div style="margin-bottom: 6px; color: black; font-weight: bold;">
            📍 ${center.lat.toFixed(5)}, ${center.lng.toFixed(5)}
          </div>
          <a 
            href="${destinationUrl}" 
            target="_blank" 
            style="
              display: inline-block;
              padding: 6px 12px;
              background-color: #ff5722;
              color: white;
              text-decoration: none;
              border-radius: 4px;
              font-size: 13px;
              margin-bottom: 6px;
            "
          >
            Route anzeigen
          </a>
        </div>
      `,
      pixelOffset: new google.maps.Size(0, -40), // shift upward, stays horizontally centered
    });
    

    markerDiv.addEventListener('click', (e) => {
      e.stopPropagation();
      infoWindow.open({ map, anchor: marker });
    });

    map.addListener('click', () => {
      infoWindow.close();
    });
  }, []);

  return (
    <div style={divStyle}>
      <LoadScript
        googleMapsApiKey="AIzaSyDu-dTYm2TIAQm6-ViVIpL8gKiVHCvfWhE"
        libraries={['marker']}
      >
        <GoogleMap
          mapContainerStyle={containerStyle}
          center={center}
          zoom={14}
          onLoad={onLoad}

          options={{
            mapId: 'a1c37327e521572c',
          }}
        />
      </LoadScript>

    </div>
    
  );
};

export default MapComponent;
