const map = new maplibregl.Map({
    container: 'map',
    style: 'https://demotiles.maplibre.org/style.json',
    center: [0, 20],
    zoom: 1.5
});

map.on('load', () => {

    map.setProjection({
        type: 'globe'
    });

    fetch('https://version2.ice-d.org/api/leaflet_map/alpine?format=json')
        .then(response => response.json())
        .then(mapPayload => {

            map.addSource('alpine-points', {
                type: 'geojson',
                data: mapPayload
            });

            map.addLayer({
                id: 'alpine-points',
                type: 'circle',
                source: 'alpine-points',

                paint: {
                    'circle-radius': 5,
                    'circle-color': '#ff0000',
                    'circle-opacity': 0.8
                }
            });

        });

});