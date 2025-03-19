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
		value: 10,
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
		value: 80,
	},
];

// Funkcja do wyboru ikony na podstawie typu szkoły
const getIcon = (type: string) => {
	switch (type) {
		case "Technikum":
			return "/icons/technik.png";
		case "Liceum":
			return "/icons/liceum.png";
		case "Zawodowka":
			return "/icons/zawodowka.png";
		default:
			return "/icons/default.png";
	}
};

// Funkcja do obliczenia odcienia na podstawie wartości (0-100)
const getHueRotation = (value: number) => {
	if (value <= 25) return 0;
	if (value <= 50) return 30;
	if (value <= 75) return 60;
	return 120;
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

	schools.forEach((school) => {
		const el = document.createElement("div");
		el.className = "custom-marker";
		el.style.backgroundImage = `url(${getIcon(school.type)})`;
		el.style.backgroundSize = "contain";
		el.style.width = "128px";
		el.style.height = "128px";

		// Dynamiczne filtrowanie kolorów ikon
		el.style.filter = `hue-rotate(${getHueRotation(school.value)}deg)`;

		new maplibregl.Marker({ element: el })
			.setLngLat([school.lon, school.lat])
			.setPopup(
				new maplibregl.Popup().setText(
					`${school.name} (Wartość: ${school.value})`,
				),
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
}

@media (max-width: 768px) {
	#map {
		width: 95vw;
		height: 60vh;
	}
}
</style>
