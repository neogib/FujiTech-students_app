<script setup lang="ts">
import type { Feature, Point } from "geojson"

interface SchoolProperties {
    score: number
    description: string
}

// Reactive state for sidebar
const isSidebarOpen = ref(false)
const selectedPoint = ref<Feature<Point, SchoolProperties> | null>(null)

const handlePointClick = (feature: Feature<Point, SchoolProperties>) => {
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

        <!-- MapView taking full remaining space with dynamic margin for sidebar -->
        <div
            :class="[
                'transition-all duration-300',
                isSidebarOpen ? 'lg:ml-80' : 'ml-0',
            ]">
            <MapView @point-clicked="handlePointClick" />
        </div>
    </div>
</template>
