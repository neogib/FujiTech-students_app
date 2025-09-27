<script setup lang="ts">
import type { Feature, Point } from "geojson"
import type { SchoolShort } from "~/types/schools"

interface Props {
    isOpen: boolean
    selectedPoint: Feature<Point, SchoolShort> | null
}

defineProps<Props>()

// Define emits for closing the sidebar
const emit = defineEmits<{
    close: []
}>()

const closeSidebar = () => {
    emit("close")
}
</script>

<template>
    <div
        :class="[
            'fixed top-0 left-0 h-full bg-white shadow-lg transition-transform duration-300 z-50',
            'w-80 border-r border-gray-200',
            isOpen ? 'transform translate-x-0' : 'transform -translate-x-full',
        ]">
        <!-- Sidebar Header -->
        <div
            class="flex items-center justify-between p-4 border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-900">School Details</h2>
            <button
                class="p-2 rounded-md hover:bg-gray-100 transition-colors"
                aria-label="Close sidebar"
                @click="closeSidebar">
                <svg
                    class="w-5 h-5 text-gray-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24">
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        </div>

        <!-- Sidebar Content -->
        <div class="p-4">
            <div v-if="selectedPoint" class="space-y-4">
                <!-- Score Display -->
                <div class="bg-gray-50 rounded-lg p-4">
                    <h3 class="text-sm font-medium text-gray-700 mb-2">
                        School Score
                    </h3>
                    <div class="flex items-center space-x-3">
                        <div
                            :class="[
                                'text-2xl font-bold',
                                selectedPoint.properties.score >= 75
                                    ? 'text-green-600'
                                    : selectedPoint.properties.score >= 50
                                      ? 'text-yellow-600'
                                      : 'text-red-600',
                            ]">
                            {{ selectedPoint.properties.score }}
                        </div>
                        <div class="text-sm text-gray-500">/ 100</div>
                    </div>

                    <!-- Score Bar -->
                    <div class="mt-3">
                        <div class="w-full bg-gray-200 rounded-full h-2">
                            <div
                                :class="[
                                    'h-2 rounded-full transition-all duration-300',
                                    selectedPoint.properties.score >= 75
                                        ? 'bg-green-500'
                                        : selectedPoint.properties.score >= 50
                                          ? 'bg-yellow-500'
                                          : 'bg-red-500',
                                ]"
                                :style="{
                                    width: `${selectedPoint.properties.score}%`,
                                }" />
                        </div>
                    </div>
                </div>

                <!-- Location Information -->
                <div class="bg-gray-50 rounded-lg p-4">
                    <h3 class="text-sm font-medium text-gray-700 mb-2">
                        Location
                    </h3>
                    <div class="text-sm text-gray-600 space-y-1">
                        <div>
                            <span class="font-medium">Latitude:</span>
                            {{
                                selectedPoint.geometry.coordinates[1].toFixed(6)
                            }}
                        </div>
                        <div>
                            <span class="font-medium">Longitude:</span>
                            {{
                                selectedPoint.geometry.coordinates[0].toFixed(6)
                            }}
                        </div>
                    </div>
                </div>

                <!-- Description -->
                <div class="bg-gray-50 rounded-lg p-4">
                    <h3 class="text-sm font-medium text-gray-700 mb-2">
                        Description
                    </h3>
                    <div class="text-sm text-gray-600">
                        {{ selectedPoint.properties.nazwa }}
                    </div>
                </div>

                <!-- Performance Category -->
                <div class="bg-gray-50 rounded-lg p-4">
                    <h3 class="text-sm font-medium text-gray-700 mb-2">
                        Performance Category
                    </h3>
                    <span
                        :class="[
                            'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                            selectedPoint.properties.score >= 75
                                ? 'bg-green-100 text-green-800'
                                : selectedPoint.properties.score >= 50
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : 'bg-red-100 text-red-800',
                        ]">
                        {{
                            selectedPoint.properties.score >= 75
                                ? "Excellent"
                                : selectedPoint.properties.score >= 50
                                  ? "Good"
                                  : "Needs Improvement"
                        }}
                    </span>
                </div>
            </div>
        </div>
    </div>

    <!-- Overlay for mobile -->
    <div
        v-if="isOpen"
        class="fixed inset-0 bg-black opacity-25 z-40 lg:hidden"
        @click="closeSidebar" />
</template>
