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

const getShape = (type: string): string => {
	switch (type) {
		case "Technikum":
			return "square";
		case "Liceum":
			return "circle";
		case "Zawodowka":
			return "triangle";
		default:
			return "circle";
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
		el.className = `custom-marker shape-${getShape(school.type)}`;
		el.style.backgroundColor = getColorForValue(school.value);
		el.style.width = "24px";
		el.style.height = "24px";
		el.style.border = "2px solid white";
		el.style.boxShadow = "0 0 4px #000";

		const count = locationCountMap.get(`${school.lat},${school.lon}`) || 1;
		el.title = `${school.name} (Wartość: ${school.value})\nSzkół w tym miejscu: ${count}`;

		new maplibregl.Marker({ element: el })
			.setLngLat([school.lon, school.lat])
			.setPopup(
				new maplibregl.Popup().setText(
					`${school.name} (Wartość: ${school.value})\nSzkół w tym miejscu: ${count}`
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

.shape-circle {
	border-radius: 50%;
}

.shape-square {
	border-radius: 4px;
}

.shape-triangle {
	width: 0;
	height: 0;
	border-left: 12px solid transparent;
	border-right: 12px solid transparent;
	border-bottom: 24px solid currentColor;
	background-color: transparent;
	box-shadow: none;
	border-radius: 0;
}

@media (max-width: 768px) {
	#map {
		width: 95vw;
		height: 60vh;
	}
}
</style>