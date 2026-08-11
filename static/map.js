const map = new maplibregl.Map({
    container: 'map',
    style: 'https://demotiles.maplibre.org/style.json',
    center: [-90, 20],
    zoom: 1.5,
    pitch: 30,
    projection: 'globe'
});