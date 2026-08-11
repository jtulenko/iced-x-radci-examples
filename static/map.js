const map = new maplibregl.Map({
    container: 'map',
    style: 'https://demotiles.maplibre.org/style.json',
    center: [0, 20],
    zoom: 1.5
});

map.on('load', () => {

    // Set the map to a 3D globe
    map.setProjection({
        type: 'globe'
    });

    // Load sample data from the API
    fetch('https://version2.ice-d.org/api/leaflet_map/alpine?format=json')
        .then(response => response.json())
        .then(mapPayload => {

            // API returns JSON encoded as a string,
            // so parse it a second time.
            mapPayload = JSON.parse(mapPayload);

            // Add the sample data as a GeoJSON source
            map.addSource('iced-samples', {
                type: 'geojson',
                data: mapPayload.samples
            });

            // Add sample points
            map.addLayer({
                id: 'iced-samples',
                type: 'circle',
                source: 'iced-samples',
                paint: {
                    'circle-radius': 5,
                    'circle-color': '#800020',
                    'circle-opacity': 0.8,
                    'circle-stroke-color': '#000000',
                    'circle-stroke-width': 1,
                    'circle-stroke-opacity': 1
                }
            });

            // Change cursor when hovering over a sample
            map.on('mouseenter', 'iced-samples', () => {
                map.getCanvas().style.cursor = 'pointer';
            });

            map.on('mouseleave', 'iced-samples', () => {
                map.getCanvas().style.cursor = '';
            });

            // Display all properties when a sample is clicked
            map.on('click', 'iced-samples', (e) => {

                const properties = e.features[0].properties;

                let popupHTML = '';

                for (const [key, value] of Object.entries(properties)) {
                    popupHTML += `<strong>${key}:</strong> ${value}<br>`;
                }

                new maplibregl.Popup()
                    .setLngLat(e.lngLat)
                    .setHTML(popupHTML)
                    .addTo(map);
            });

        });

    // Reset map button
    document.getElementById('reset-map').addEventListener('click', () => {

        map.flyTo({
            center: [0, 0],
            zoom: 1.5,
            pitch: 0
        });

    });

});