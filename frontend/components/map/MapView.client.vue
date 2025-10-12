<script setup lang="ts">
import type { LngLatBoundsLike } from "maplibre-gl"
import { MAP_CONFIG, ICON_URLS } from "~/constants/mapConfig"
import type { SzkolaPublic, SzkolaPublicShort } from "~/types/schools"

const props = defineProps<{
    schools: SzkolaPublicShort[] | null
}>()

const emit = defineEmits<{
    "point-clicked": [school: SzkolaPublic]
}>()

const { bbox, updateBbox } = useBoundingBox()
const { geoJsonSource } = useSchoolGeoJson(toRef(props, "schools"))
const { setupMapEventHandlers } = useMapInteractions(emit, updateBbox)

const bounds: LngLatBoundsLike | undefined = !bbox
    ? undefined
    : [
          [bbox.min_lng, bbox.min_lat],
          [bbox.max_lng, bbox.max_lat],
      ]

const onMapLoaded = (event: { map: maplibregl.Map }) => {
    setupMapEventHandlers(event.map)
}
</script>

<template>
    <MglMap
        :map-style="MAP_CONFIG.style"
        :center="MAP_CONFIG.defaultCenter"
        :zoom="MAP_CONFIG.defaultZoom"
        :max-bounds="MAP_CONFIG.polandBounds"
        :bounds="bounds"
        height="100vh"
        @map:load="onMapLoaded">
        <MglNavigationControl />

        <MglImage
            v-for="iconUrl in ICON_URLS"
            :id="`${iconUrl.split('/').pop()?.split('.').shift()}_sdf`"
            :key="iconUrl"
            :url="iconUrl"
            :options="{ sdf: true }" />

        <MapSchoolLayers :source-data="geoJsonSource" />
    </MglMap>
</template>
