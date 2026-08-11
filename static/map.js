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
});