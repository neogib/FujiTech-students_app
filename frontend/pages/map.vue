<script setup lang="ts">
import type { Feature, Point } from "geojson"
import type { SchoolShort } from "~/types/schools"

const router = useRoute()
const { data, status } = useApi<SchoolShort[]>("/schools", {
    query: {
        south: router.query.south,
        north: router.query.north,
        west: router.query.west,
        east: router.query.east,
        type: router.query.type,
    },
    // lazy: true,
})

// Reactive state for sidebar
const isSidebarOpen = ref(false)
const selectedPoint = ref<Feature<Point, SchoolShort> | null>(null)

const handlePointClick = (feature: Feature<Point, SchoolShort>) => {
    selectedPoint.value = feature
    isSidebarOpen.value = true
}

const handleSidebarClose = () => {
    isSidebarOpen.value = false
    selectedPoint.value = null
}
</script>

<template>
    <div>
        <NavBar transparent />

        <!-- Sidebar -->
        <MapSidebar
            :is-open="isSidebarOpen"
            :selected-point="selectedPoint"
            @close="handleSidebarClose" />
        <UserMessage
            v-if="status === 'pending'"
            message="Loading map data, please wait..." />
        <UserMessage
            v-if="status === 'error'"
            type="error"
            message="An error occurred while loading map data." />

        <!-- MapView taking full remaining space with dynamic margin for sidebar -->
        <div
            :class="[
                'transition-all duration-300',
                isSidebarOpen ? 'lg:ml-80' : 'ml-0',
            ]">
            <MapView :schools="data" @point-clicked="handlePointClick" />
        </div>
    </div>
</template>
