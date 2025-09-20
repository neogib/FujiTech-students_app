<script setup lang="ts">
import maplibregl from "maplibre-gl"
import triangleIconUrl from "~/assets/images/triangle_small.png"
import type { FeatureCollection, Feature, Point } from "geojson"

const style = "https://tiles.openfreemap.org/styles/liberty"
const center: [number, number] = [-77.04, 38.907]
const zoom = 11.15

interface SchoolProperties {
    score: number
    description: string
}

// Define emits for the component
const emit = defineEmits<{
    "point-clicked": [feature: Feature<Point, SchoolProperties>]
}>()

const features: Feature<Point, SchoolProperties>[] = []

for (let i = 0; i < 100; i++) {
    const randomScore = Math.floor(Math.random() * 101)
    features.push({
        type: "Feature",
        properties: {
            score: randomScore,
            description: `<strong>Random Point ${i + 1}</strong><p>This is a randomly generated point with a score of ${randomScore}.</p>`,
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

// Properly type the GeoJSON source as FeatureCollection
const geoJsonSource: FeatureCollection<Point, SchoolProperties> = {
    type: "FeatureCollection",
    features: features,
}

const onMapLoaded = (event: { map: maplibregl.Map }) => {
    const popup = new maplibregl.Popup({
        closeButton: false,
        closeOnClick: false,
    })
    const map = event.map
    let currentFeatureCoordinates: string | undefined = undefined
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

    // Add click event handler
    map.on("click", "my-interactive-layer", (e) => {
        const feature_collection = e.features?.[0]
        if (
            !feature_collection ||
            feature_collection.geometry.type !== "Point"
        ) {
            return
        }

        // Type the feature properly and emit the click event
        // Convert to unknown first to safely cast from MapGeoJSONFeature to our specific type
        const clickedFeature = feature_collection as unknown as Feature<
            Point,
            SchoolProperties
        >
        emit("point-clicked", clickedFeature)
    })
}
</script>
<template>
    <MglMap
        :map-style="style"
        :center="center"
        :zoom="zoom"
        height="100vh"
        @map:load="onMapLoaded">
        <MglNavigationControl />

        <mgl-image
            id="triangle_sdf"
            :url="triangleIconUrl"
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
                    'icon-image': 'triangle_sdf',
                    'icon-overlap': 'always',
                }" />
        </MglGeoJsonSource>
    </MglMap>
</template>
