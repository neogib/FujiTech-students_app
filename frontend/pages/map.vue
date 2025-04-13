<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { useRspo } from "~/composables/fetcher";
import type { School } from "~/types/rspo";

const { institutions, isLoading, error, fetchInstitutions } = useRspo();
const map = ref(null);
const schools = ref<School[]>([]);

// Fetch data when component mounts
onMounted(async () => {
  await fetchInstitutions("/placowki/", {
    method: "GET",
	params: {
	  page: 3,
	}, 
  });
  console.log("Data fetched:", institutions.value?.length || 0, "institutions");
});

// Process data when it becomes available
watch(institutions, (newInstitutions) => {
  if (newInstitutions && newInstitutions.length > 0) {
    console.log("Processing", newInstitutions.length, "institutions");
    
    // Map the institutions to schools format
    schools.value = newInstitutions.map((school) => {
      return {
        name: school.nazwa,
        type: school.typ.nazwa,
        lat: school.geolokalizacja.latitude,
        lon: school.geolokalizacja.longitude,
        value: Math.floor(Math.random() * 100),
      };
    })
    // Initialize map after data is processed
    initializeMap();
  }
}, { deep: true });

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

// Move map initialization to a separate function that's called after data is processed
const initializeMap = () => {
  if (map.value) return; // Avoid initializing twice
  
  console.log("Initializing map with", schools.value.length, "schools");
  
  map.value = new maplibregl.Map({
    container: "map",
    style: "https://tiles.openfreemap.org/styles/liberty",
    center: [21.0118, 52.2298],
    zoom: 7,
    maxBounds: [
      [14.0, 49.0],
      [24.2, 55.0],
    ],
  });
  
  map.value.addControl(new maplibregl.NavigationControl());
  
  // Wait for the map to load before adding markers
  map.value.on('load', () => {
    schools.value.forEach((school) => {
      const el = document.createElement("div");
      el.className = "custom-marker";
      el.style.backgroundImage = `url(${getIcon(school.type)})`;
      el.style.backgroundSize = "contain";
      el.style.width = "32px"; // Reduced size from 128px
      el.style.height = "32px"; // Reduced size for better usability
      
      // Dynamiczne filtrowanie kolorów ikon
      el.style.filter = `hue-rotate(${getHueRotation(school.value)}deg)`;
      
      new maplibregl.Marker({ element: el })
        .setLngLat([school.lon, school.lat])
        .setPopup(
          new maplibregl.Popup().setText(
            `${school.name} (Wartość: ${school.value})`,
          ),
        )
        .addTo(map.value);
    });
  });
};
</script>

<template>
  <div class="map-container">
    <h1>Mapa OpenStreetMap (MapLibre) - Szkoły</h1>
    <div v-if="isLoading" class="status-message loading">Ładowanie danych...</div>
    <div v-else-if="error" class="status-message error">Błąd: {{ error.message }}</div>
    <div v-else-if="schools.length === 0" class="status-message">Brak szkół do wyświetlenia</div>
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
  cursor: pointer;
}

.status-message {
  margin: 10px 0;
  padding: 10px;
  border-radius: 4px;
  text-align: center;
}

.loading {
  background-color: #e3f2fd;
}

.error {
  background-color: #ffebee;
  color: #c62828;
}

@media (max-width: 768px) {
  #map {
    width: 95vw;
    height: 60vh;
  }
}
</style>
