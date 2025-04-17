<script setup lang="ts">
import { onMounted } from "vue";
// Correct: Only import the default export and the CSS
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css"; // Make sure CSS is loaded (can be here or nuxt.config.ts)

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
        // Note: Same coordinates as the first one, will overlap
        lat: 52.2298,
        lon: 21.0118,
        type: "Technikum",
        value: 70,
    },
];

const getColorForValue = (value: number): string => {
    // Ensure value stays within 0-100 for calculation if needed
    const clampedValue = Math.max(0, Math.min(100, value));
    const red = clampedValue < 50 ? 255 : Math.round(255 - ((clampedValue - 50) * 5.1));
    const green = clampedValue > 50 ? 255 : Math.round(clampedValue * 5.1);
    return `rgb(${red},${green},0)`;
};

const getShapeSVG = (type: string): string => {
    // Using currentColor allows the SVG fill to inherit the color set via CSS
    switch (type) {
        case "Technikum":
            return "<rect width='24' height='24' style='fill:currentColor;stroke:black;stroke-width:1;'/>"; // Adjusted stroke for visibility
        case "Liceum":
            return "<circle cx='12' cy='12' r='11' style='fill:currentColor;stroke:black;stroke-width:1;'/>"; // Adjusted stroke/radius
        case "Zawodowka":
            return "<polygon points='12,2 22,22 2,22' style='fill:currentColor;stroke:black;stroke-width:1;'/>"; // Adjusted points/stroke
        default:
            return "<circle cx='12' cy='12' r='11' style='fill:currentColor;stroke:black;stroke-width:1;'/>"; // Default with stroke
    }
};

onMounted(() => {
    // This code runs only on the client-side after the component is mounted
    const map = new maplibregl.Map({
        container: "map", // The ID of the div in the template
        style: "https://tiles.openfreemap.org/styles/liberty", // Base map style
        center: [21.0118, 52.2298], // Initial map center [Lon, Lat]
        zoom: 6, // Adjusted initial zoom to see more schools
        maxBounds: [ // Optional: constrain map panning
            [14.0, 49.0], // Southwest coordinates
            [24.2, 55.0], // Northeast coordinates
        ],
    });

    // Add controls using the main maplibregl object
    map.addControl(new maplibregl.NavigationControl(), 'top-right'); // Position controls
    map.addControl(new maplibregl.FullscreenControl(), 'top-right'); // Position controls

    // Create and add markers to the map
    schools.forEach((school) => {
        // 1. Create the custom HTML element for the marker
        const el = document.createElement("div");
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("viewBox", "0 0 24 24"); // Added viewBox for better scaling
        svg.setAttribute("width", "24");
        svg.setAttribute("height", "24");
        svg.innerHTML = getShapeSVG(school.type); // Generate the SVG shape string
        el.appendChild(svg);
        el.style.color = getColorForValue(school.value); // Set SVG fill via CSS 'color' property
        el.style.width = "24px";
        el.style.height = "24px";
        el.style.cursor = 'pointer'; // Make it look clickable
        el.title = school.name; // Add a hover title

        // 2. Create the MapLibre Marker, assign the custom element, set position, add popup, and add to map
        new maplibregl.Marker({ element: el })
            .setLngLat([school.lon, school.lat]) // Set marker position [Lon, Lat]
            .setPopup(new maplibregl.Popup({ offset: 25 }) // Create a popup, offset slightly
                .setHTML(`<h3>${school.name}</h3><p>Typ: ${school.type}<br>Wartość: ${school.value}</p>`) // Set popup content
            )
            .addTo(map); // Add the marker instance to the map
    });
});
</script>

<template>
    <div class="map-container">
        <h1>Mapa OpenStreetMap (MapLibre) - Szkoły</h1>
        <!-- This div is the target for the map -->
        <div id="map"></div>
    </div>
</template>

<style scoped>
.map-container {
    width: 100%;
    /* Using vh units can be tricky, consider flex or grid parent if needed */
    height: 90vh; /* Make container take significant height */
    display: flex;
    flex-direction: column;
    align-items: center; /* Center map horizontally */
    padding: 1rem; /* Add some padding around */
    box-sizing: border-box;
}

#map {
    width: 100%; /* Map takes full width of container */
    max-width: 1200px; /* Optional: constrain max width */
    height: 100%; /* Map takes full height of container */
    border: 1px solid #ccc;
    border-radius: 8px;
}

</style>