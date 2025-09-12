<template>
    <MglMap :map-style="style" :center="center" :zoom="zoom" height="100vh">
        <MglNavigationControl />
    </MglMap>
</template>

<script setup>
import "maplibre-gl/dist/maplibre-gl.css";
import { MglMap, MglNavigationControl } from "@indoorequal/vue-maplibre-gl";

const style = "https://tiles.openfreemap.org/styles/liberty";
const center = [12.550343, 55.665957];
const zoom = 8;
</script>
