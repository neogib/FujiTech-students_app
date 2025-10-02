<script setup lang="ts">
import maplibregl from "maplibre-gl"
import triangleIconUrl from "~/assets/images/figures/triangle.png"
import circleIconUrl from "~/assets/images/figures/circle.png"
import diamondIconUrl from "~/assets/images/figures/diamond.png"
import squareIconUrl from "~/assets/images/figures/square.png"
import starIconUrl from "~/assets/images/figures/star.png"
import type { FeatureCollection, Feature, Point } from "geojson"
import type { SchoolShort } from "~/types/schools"
const iconUrls = [
    triangleIconUrl,
    circleIconUrl,
    diamondIconUrl,
    squareIconUrl,
    starIconUrl,
]
console.log("Icon URLs:", iconUrls)

const style = "https://tiles.openfreemap.org/styles/liberty"
const center: [number, number] = [19, 52]
const zoom = 6
const route = useRoute()

const props = defineProps<{
    schools: SchoolShort[] | null
}>()

// Define emits for the component
const emit = defineEmits<{
    "point-clicked": [feature: Feature<Point, SchoolShort>]
}>()

/**
 * Transform SchoolShort objects to GeoJSON features
 * @param schools - Array of SchoolShort objects
 * @returns Array of GeoJSON features
 */
const transformSchoolsToFeatures = (
    schools: SchoolShort[],
): Feature<Point, SchoolShort>[] => {
    return schools.map((school) => ({
        type: "Feature",
        properties: school,
        geometry: {
            type: "Point",
            coordinates: [
                school.geolokalizacja_longitude,
                school.geolokalizacja_latitude,
            ],
        },
    }))
}

// Create reactive GeoJSON source that updates when schools prop changes
const geoJsonSource = computed<FeatureCollection<Point, SchoolShort>>(() => {
    const features = props.schools
        ? transformSchoolsToFeatures(props.schools)
        : []

    return {
        type: "FeatureCollection",
        features,
    }
})

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
            const feature_properties: SchoolShort =
                feature_collection.properties as SchoolShort
            const description = `${feature_properties.nazwa} ${feature_properties.numer_rspo} ${feature_properties.geolokalizacja_latitude} ${feature_properties.geolokalizacja_longitude}`
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

    // --- DEBOUNCING LOGIC ---
    let debounceTimeout: NodeJS.Timeout | null = null

    const updateQueryParams = async () => {
        console.log("Map movement settled, updating route params...")
        const bounds = map.getBounds()
        await navigateTo({
            query: {
                ...route.query,
                south: bounds.getSouth().toString(),
                north: bounds.getNorth().toString(),
                west: bounds.getWest().toString(),
                east: bounds.getEast().toString(),
            },
            replace: true,
        })
    }

    map.on("moveend", () => {
        // Clear the previous timeout if it exists
        if (debounceTimeout) {
            clearTimeout(debounceTimeout)
        }

        // Set a new timeout
        debounceTimeout = setTimeout(() => {
            updateQueryParams()
        }, 300) // Wait for 300ms of inactivity before fetching
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
            SchoolShort
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
            v-for="iconUrl in iconUrls"
            :id="`${iconUrl.split('/').pop()?.split('.').shift()}_sdf`"
            :key="iconUrl"
            :url="iconUrl"
            :options="{ sdf: true }" />

        <!-- Add your MglSource and MglLayer components here -->
        <MglGeoJsonSource
            source-id="my-data-source"
            :data="geoJsonSource"
            :cluster="true"
            :cluster-properties="{
                // Calculate sum of scores
                sum: ['+', ['get', 'score']],
            }">
            <MglSymbolLayer
                layer-id="my-interactive-layer"
                :paint="{
                    'icon-color': [
                        'interpolate',
                        ['linear'],
                        [
                            'case',
                            ['has', 'cluster'],
                            // If it's a cluster, calculate average: sum / point_count
                            ['/', ['get', 'sum'], ['get', 'point_count']],
                            // If it's not a cluster, use the regular score
                            ['get', 'score'],
                        ],
                        0,
                        '#FF0000', // red at 0
                        50,
                        '#FFFF00', // yellow at 50
                        100,
                        '#00FF00', // green at 100
                    ],
                }"
                :layout="{
                    'icon-image': [
                        'case',
                        ['has', 'cluster'],
                        'star_sdf',
                        ['==', ['get', 'nazwa', ['get', 'typ']], 'Technikum'],
                        'triangle_sdf',
                        [
                            '==',
                            ['get', 'nazwa', ['get', 'typ']],
                            'Liceum ogólnokształcące',
                        ],
                        'circle_sdf',
                        [
                            '==',
                            ['get', 'nazwa', ['get', 'typ']],
                            'Szkoła podstawowa',
                        ],
                        'square_sdf',
                        ['==', ['get', 'nazwa', ['get', 'typ']], 'Przedszkole'],
                        'diamond_sdf',
                        // Default fallback for any other school types
                        'star_sdf',
                    ],
                    'icon-overlap': 'always',
                }" />
        </MglGeoJsonSource>
    </MglMap>
</template>
