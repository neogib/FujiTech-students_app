<template>
    <img
        ref="triangle"
        src="~/assets/images/triangle.svg"
        alt="triangle"
        class="hidden" />
    <MglMap
        :map-style="style"
        :center="center"
        :zoom="zoom"
        height="100vh"
        @map:load="onMapLoaded">
        <MglNavigationControl />

        <mgl-image
            id="custom-marker"
            :image="triangle as HTMLImageElement"
            :options="{ sdf: true }" />

        <!-- Add your MglSource and MglLayer components here -->
        <MglGeoJsonSource
            source-id="my-data-source"
            :data="geoJsonSource"
            :cluster="true">
            <MglSymbolLayer
                layer-id="my-interactive-layer"
                :paint="{
                    'icon-color': [
                        'interpolate',
                        ['linear'],
                        ['get', 'score'],
                        0,
                        '#FF0000', // red at 0
                        50,
                        '#FFFF00', // yellow at 50
                        100,
                        '#00FF00', // green at 100
                    ],
                }"
                :layout="{
                    'icon-image': 'custom-marker',
                    'icon-overlap': 'always',
                }" />
        </MglGeoJsonSource>
    </MglMap>
</template>

<script setup lang="ts">
import "maplibre-gl/dist/maplibre-gl.css"
import {
    MglMap,
    MglNavigationControl,
    MglGeoJsonSource,
    MglSymbolLayer,
} from "@indoorequal/vue-maplibre-gl"
import maplibregl from "maplibre-gl"

const triangle = useTemplateRef("triangle")
const popup = new maplibregl.Popup({
    closeButton: false,
    closeOnClick: false,
})

const style = "https://tiles.openfreemap.org/styles/liberty"
const center: [number, number] = [-77.04, 38.907]
const zoom = 11.15

const onMapLoaded = (event: { map: maplibregl.Map }) => {
    let currentFeatureCoordinates: string | undefined = undefined
    const map = event.map
    map.on("mousemove", "my-interactive-layer", (e) => {
        const feature_collection = e.features?.[0]
        if (
            !feature_collection ||
            feature_collection.geometry.type !== "Point"
        ) {
            return
        }

        // Type assertion since we've already checked that geometry.type is 'Point'
        const pointGeometry = feature_collection.geometry
        const featureCoordinates = pointGeometry.coordinates.toString()
        if (currentFeatureCoordinates !== featureCoordinates) {
            currentFeatureCoordinates = featureCoordinates

            // Change the cursor style as a UI indicator.
            map.getCanvas().style.cursor = "pointer"

            const coordinates = pointGeometry.coordinates.slice()
            const description = feature_collection.properties?.description

            // Ensure that if the map is zoomed out such that multiple
            // copies of the feature are visible, the popup appears
            // over the copy being pointed to.
            while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360
            }

            // Populate the popup and set its coordinates
            // based on the feature found.
            popup
                .setLngLat(coordinates as [number, number])
                .setHTML(description)
                .addTo(map)
        }
    })

    map.on("mouseleave", "my-interactive-layer", () => {
        currentFeatureCoordinates = undefined
        map.getCanvas().style.cursor = ""
        popup.remove()
    })
}

const features = []

for (let i = 0; i < 100; i++) {
    features.push({
        type: "Feature",
        properties: {
            score: Math.floor(Math.random() * 101), // Random score between 0 and 100
            description: `<strong>Random Point ${i + 1}</strong><p>This is a randomly generated point with a score of ${Math.floor(
                Math.random() * 101,
            )}.</p>`,
        },
        geometry: {
            type: "Point",
            coordinates: [
                -77.04 + (Math.random() - 0.5) * 0.2, // Random longitude around center
                38.907 + (Math.random() - 0.5) * 0.2, // Random latitude around center
            ],
        },
    })
}

const geoJsonSource = {
    type: "FeatureCollection",
    features: features,
}
</script>
