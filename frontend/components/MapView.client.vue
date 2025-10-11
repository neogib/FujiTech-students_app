<script setup lang="ts">
import maplibregl from "maplibre-gl"
import type { LngLatBoundsLike } from "maplibre-gl"
import triangleIconUrl from "~/assets/images/figures/triangle.png"
import diamondIconUrl from "~/assets/images/figures/diamond.png"
import squareIconUrl from "~/assets/images/figures/square.png"
import starIconUrl from "~/assets/images/figures/star.png"
import hexagonIconUrl from "~/assets/images/figures/hexagon.png"
import type { FeatureCollection, Feature, Point } from "geojson"
import type { SzkolaPublicShort, SzkolaPublic } from "~/types/schools"

const iconUrls = [
    triangleIconUrl,
    diamondIconUrl,
    squareIconUrl,
    starIconUrl,
    hexagonIconUrl,
]
const props = defineProps<{
    schools: SzkolaPublicShort[] | null
}>()

const emit = defineEmits<{
    "point-clicked": [school: SzkolaPublic]
}>()

const style = "https://tiles.openfreemap.org/styles/liberty"

const center = ref<[number, number]>([19, 52]) // Default value
const { bbox, updateBbox: updateQueryBboxParam } = useBoundingBox()
const bounds: LngLatBoundsLike | undefined = !bbox
    ? undefined
    : [
          [bbox.min_lng, bbox.min_lat],
          [bbox.max_lng, bbox.max_lat],
      ]

const polandBounds: LngLatBoundsLike = [
    [14.0, 49], // Southwest
    [24.5, 55.2], // Northeast
]
const zoom = 8

// Transform SchoolShort objects to GeoJSON features
const transformSchoolsToFeatures = (
    schools: SzkolaPublicShort[],
): Feature<Point, SzkolaPublicShort>[] => {
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
const geoJsonSource = computed<FeatureCollection<Point, SzkolaPublicShort>>(
    () => {
        const features = props.schools
            ? transformSchoolsToFeatures(props.schools)
            : []

        return {
            type: "FeatureCollection",
            features,
        }
    },
)

const onMapLoaded = (event: { map: maplibregl.Map }) => {
    const popup = new maplibregl.Popup({
        closeButton: false,
        closeOnClick: false,
    })
    const map = event.map
    let currentFeatureCoordinates: string | undefined = undefined
    map.on("mousemove", "unclustered-points", (e) => {
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

            const coordinates = pointGeometry.coordinates.slice() as [
                number,
                number,
            ]
            const feature_properties: SzkolaPublicShort =
                feature_collection.properties as SzkolaPublicShort
            // TODO: customize popup content
            const description = `${feature_properties.nazwa} ${feature_properties.numer_rspo} ${feature_properties.geolokalizacja_latitude} ${feature_properties.geolokalizacja_longitude} score: ${feature_properties.score}`

            // Ensure that if the map is zoomed out such that multiple
            // copies of the feature are visible, the popup appears
            // over the copy being pointed to.
            while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360
            }

            // Populate the popup and set its coordinates
            // based on the feature found.
            popup.setLngLat(coordinates).setHTML(description).addTo(map)
        }
    })

    map.on("mouseleave", "unclustered-points", () => {
        currentFeatureCoordinates = undefined
        map.getCanvas().style.cursor = ""
        popup.remove()
    })

    // --- DEBOUNCING LOGIC ---
    let debounceTimeout: NodeJS.Timeout | null = null

    map.on("moveend", () => {
        // Clear the previous timeout if it exists
        if (debounceTimeout) {
            clearTimeout(debounceTimeout)
        }

        // Set a new timeout
        debounceTimeout = setTimeout(() => {
            updateQueryBboxParam(map.getBounds())
        }, 300) // Wait for 300ms of inactivity before fetching
    })
    // Add click event handler
    map.on("click", "unclustered-points", async (e) => {
        const feature_collection = e.features?.[0]

        const schoolFullDetails = await useApi<SzkolaPublic>(
            `/schools/${feature_collection?.properties.id}`,
        )
        console.log("Clicked feature details:", schoolFullDetails.data)

        if (schoolFullDetails.data.value) {
            emit("point-clicked", schoolFullDetails.data.value)
        }
    })
}
</script>
<template>
    <MglMap
        :map-style="style"
        :center="center"
        :zoom="zoom"
        :max-bounds="polandBounds"
        :bounds="bounds"
        height="100vh"
        @map:load="onMapLoaded">
        <MglNavigationControl />

        <mgl-image
            v-for="iconUrl in iconUrls"
            :id="`${iconUrl.split('/').pop()?.split('.').shift()}_sdf`"
            :key="iconUrl"
            :url="iconUrl"
            :options="{ sdf: true }" />

        <MglGeoJsonSource
            source-id="my-data-source"
            :data="geoJsonSource"
            :cluster="true"
            :cluster-properties="{
                sum: ['+', ['get', 'score']],
                // Count points with non-zero scores
                nonZeroCount: ['+', ['case', ['>', ['get', 'score'], 0], 1, 0]],
            }">
            <MglSymbolLayer
                layer-id="unclustered-points"
                :filter="['!', ['has', 'point_count']]"
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
                    'icon-image': [
                        'case',
                        ['==', ['get', 'nazwa', ['get', 'typ']], 'Technikum'],
                        'triangle_sdf',
                        [
                            '==',
                            ['get', 'nazwa', ['get', 'typ']],
                            'Liceum ogólnokształcące',
                        ],
                        'diamond_sdf',
                        [
                            '==',
                            ['get', 'nazwa', ['get', 'typ']],
                            'Szkoła podstawowa',
                        ],
                        'square_sdf',
                        ['==', ['get', 'nazwa', ['get', 'typ']], 'Przedszkole'],
                        'hexagon_sdf',
                        // Default fallback for any other school types
                        'star_sdf',
                    ],
                    'icon-overlap': 'always',
                }" />
            <MglCircleLayer
                layer-id="clusters"
                :filter="['has', 'cluster']"
                :paint="{
                    'circle-color': [
                        'interpolate',
                        ['linear'],
                        [
                            'case',
                            ['>', ['get', 'nonZeroCount'], 0],
                            ['/', ['get', 'sum'], ['get', 'nonZeroCount']],
                            0,
                        ],
                        0,
                        '#FF0000', // red at 0
                        50,
                        '#FFFF00', // yellow at 50
                        100,
                        '#00FF00', // green at 100
                    ],
                    'circle-radius': [
                        'step',
                        ['get', 'point_count'],
                        20,
                        100,
                        30,
                        750,
                        40,
                    ],
                }"
                }); />
            <MglSymbolLayer
                layer-id="cluster-count"
                :filter="['has', 'cluster']"
                :layout="{
                    'text-field': '{point_count_abbreviated}',
                    'text-font': ['Noto Sans Regular'],
                    'text-size': 12,
                }" />
        </MglGeoJsonSource>
    </MglMap>
</template>
