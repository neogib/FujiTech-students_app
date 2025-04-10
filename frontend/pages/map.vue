<script setup lang="ts">
import { onMounted } from "vue";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

const schools = [
    {
        name: "Technikum Elektroniczne w Warszawie",
        lat: 52.2298,
        lon: 21.0118,
        type: "Technikum",
        value: 100,
    },
    {
        name: "Liceum Ogólnokształcące w Krakowie",
        lat: 50.0614,
        lon: 19.9366,
        type: "Liceum",
        value: 45,
    },
    {
        name: "Zespół Szkół Zawodowych w Gdańsku",
        lat: 54.352,
        lon: 18.6466,
        type: "Zawodowka",
        value: 5,
    },
    {
        name: "Technikum Komunikacyjne",
        lat: 52.2298,
        lon: 21.0118,
        type: "Technikum",
        value: 70,
    },
];

const getColorForValue = (value: number): string => {
    const red = value < 50 ? 255 : Math.round(255 - ((value - 50) * 5.1));
    const green = value > 50 ? 255 : Math.round(value * 5.1);
    return `rgb(${red},${green},0)`;
};

const getShapeSVG = (type: string): string => {
    switch (type) {
        case "Technikum":
            return "<rect width='24' height='24' style='fill:currentColor;stroke:white;stroke-width:2;'/>";
        case "Liceum":
            return "<circle cx='12' cy='12' r='12' style='fill:currentColor;stroke:white;stroke-width:2;'/>";
        case "Zawodowka":
            return "<polygon points='12,0 24,24 0,24' style='fill:currentColor;stroke:white;stroke-width:2;'/>";
        default:
            return "<circle cx='12' cy='12' r='12' style='fill:currentColor;stroke:white;stroke-width:2;'/>";
    }
};

onMounted(() => {
    const map = new maplibregl.Map({
        container: "map",
        style: "https://tiles.openfreemap.org/styles/liberty",
        center: [21.0118, 52.2298],
        zoom: 7,
        maxBounds: [
            [14.0, 49.0],
            [24.2, 55.0],
        ],
    });

    map.addControl(new maplibregl.NavigationControl());

    const locationCountMap = new Map<string, number>();

    schools.forEach((school) => {
        const key = `${school.lat},${school.lon}`;
        locationCountMap.set(key, (locationCountMap.get(key) || 0) + 1);
    });

    schools.forEach((school) => {
        const el = document.createElement("div");
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("width", "24");
        svg.setAttribute("height", "24");
        svg.innerHTML = getShapeSVG(school.type);
        el.appendChild(svg);
        el.style.color = getColorForValue(school.value);
        el.style.width = "24px";
        el.style.height = "24px";
        el.style.display = "flex";
        el.style.alignItems = "center";
        el.style.justifyContent = "center";
        el.title = `${school.name} (Wartość: ${school.value})\nSzkół w tym miejscu: ${locationCountMap.get(`${school.lat},${school.lon}`) || 1}`;

        new maplibregl.Marker({ element: el })
            .setLngLat([school.lon, school.lat])
            .setPopup(
                new maplibregl.Popup().setText(
                    `${school.name} (Wartość: ${school.value})\nSzkół w tym miejscu: ${locationCountMap.get(`${school.lat},${school.lon}`) || 1}`
                )
            )
            .addTo(map);
    });
});
</script>

<template>
    <div class="map-container">
        <h1>Mapa OpenStreetMap (MapLibre) - Szkoły</h1>
        <div id="map"></div>
    </div>
</template>

<style scoped>
.map-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
}

#map {
    width: 90vw;
    max-width: 600px;
    height: 50vh;
    max-height: 500px;
    border: 2px solid #ccc;
    border-radius: 10px;
}

.custom-marker {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>
