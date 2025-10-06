<script setup lang="ts">
import type { SzkolaPublic } from "~/types/schools"

interface Props {
    isOpen: boolean
    selectedPoint: SzkolaPublic | null
}

defineProps<Props>()

// Define emits for closing the sidebar
const emit = defineEmits<{
    close: []
}>()

const closeSidebar = () => {
    emit("close")
}

// State for showing more details
const showMoreDetails = ref(false)

const toggleShowMore = () => {
    showMoreDetails.value = !showMoreDetails.value
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
            <h2 class="text-lg font-semibold text-gray-900">
                Szczegóły szkoły
            </h2>
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
                <!-- School Name -->
                <div>
                    <h3 class="text-lg font-semibold text-gray-900 mb-1">
                        {{ selectedPoint.nazwa }}
                    </h3>
                    <p class="text-sm text-gray-600">
                        RSPO: {{ selectedPoint.numer_rspo }}
                    </p>
                </div>

                <!-- Score Display -->
                <div class="bg-gray-50 rounded-lg p-4">
                    <h3 class="text-sm font-medium text-gray-700 mb-2">
                        Wynik szkoły
                    </h3>
                    <div class="flex items-center space-x-3">
                        <div
                            :class="[
                                'text-2xl font-bold',
                                selectedPoint.score >= 75
                                    ? 'text-green-600'
                                    : selectedPoint.score >= 50
                                      ? 'text-yellow-600'
                                      : 'text-red-600',
                            ]">
                            {{ selectedPoint.score }}
                        </div>
                        <div class="text-sm text-gray-500">/ 100</div>
                    </div>

                    <!-- Score Bar -->
                    <div class="mt-3">
                        <div class="w-full bg-gray-200 rounded-full h-2">
                            <div
                                :class="[
                                    'h-2 rounded-full transition-all duration-300',
                                    selectedPoint.score >= 75
                                        ? 'bg-green-500'
                                        : selectedPoint.score >= 50
                                          ? 'bg-yellow-500'
                                          : 'bg-red-500',
                                ]"
                                :style="{
                                    width: `${selectedPoint.score}%`,
                                }" />
                        </div>
                    </div>
                </div>

                <!-- Location Information -->
                <div class="bg-gray-50 rounded-lg p-4">
                    <h3 class="text-sm font-medium text-gray-700 mb-2">
                        Lokalizacja
                    </h3>
                    <div class="text-sm text-gray-600 space-y-1">
                        <div>
                            <span class="font-medium">Szerokość geogr.:</span>
                            {{
                                selectedPoint.geolokalizacja_latitude.toFixed(6)
                            }}
                        </div>
                        <div>
                            <span class="font-medium">Długość geogr.:</span>
                            {{
                                selectedPoint.geolokalizacja_longitude.toFixed(
                                    6,
                                )
                            }}
                        </div>
                        <div v-if="selectedPoint.kod_pocztowy">
                            <span class="font-medium">Kod pocztowy:</span>
                            {{ selectedPoint.kod_pocztowy }}
                        </div>
                    </div>
                </div>

                <!-- Performance Category -->
                <div class="bg-gray-50 rounded-lg p-4">
                    <h3 class="text-sm font-medium text-gray-700 mb-2">
                        Kategoria wydajności
                    </h3>
                    <span
                        :class="[
                            'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                            selectedPoint.score >= 75
                                ? 'bg-green-100 text-green-800'
                                : selectedPoint.score >= 50
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : 'bg-red-100 text-red-800',
                        ]">
                        {{
                            selectedPoint.score >= 75
                                ? "Doskonała"
                                : selectedPoint.score >= 50
                                  ? "Dobra"
                                  : "Wymaga poprawy"
                        }}
                    </span>
                </div>

                <!-- Basic Contact Info (always visible) -->
                <div
                    v-if="selectedPoint.telefon || selectedPoint.email"
                    class="bg-gray-50 rounded-lg p-4">
                    <h3 class="text-sm font-medium text-gray-700 mb-2">
                        Kontakt
                    </h3>
                    <div class="text-sm text-gray-600 space-y-1">
                        <div v-if="selectedPoint.telefon">
                            <span class="font-medium">Telefon:</span>
                            {{ selectedPoint.telefon }}
                        </div>
                        <div v-if="selectedPoint.email">
                            <span class="font-medium">Email:</span>
                            <a
                                :href="`mailto:${selectedPoint.email}`"
                                class="text-blue-600 hover:underline">
                                {{ selectedPoint.email }}
                            </a>
                        </div>
                    </div>
                </div>

                <!-- Show More Button -->
                <button
                    class="w-full bg-blue-50 hover:bg-blue-100 text-blue-700 font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2"
                    @click="toggleShowMore">
                    <span>{{
                        showMoreDetails ? "Ukryj szczegóły" : "Wyświetl więcej"
                    }}</span>
                    <svg
                        :class="[
                            'w-4 h-4 transition-transform duration-200',
                            showMoreDetails ? 'rotate-180' : '',
                        ]"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24">
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M19 9l-7 7-7-7" />
                    </svg>
                </button>

                <!-- Additional Details (shown when expanded) -->
                <div v-if="showMoreDetails" class="space-y-4">
                    <!-- Director Information -->
                    <div
                        v-if="
                            selectedPoint.dyrektor_imie ||
                            selectedPoint.dyrektor_nazwisko
                        "
                        class="bg-blue-50 rounded-lg p-4">
                        <h3 class="text-sm font-medium text-gray-700 mb-2">
                            Dyrektor
                        </h3>
                        <div class="text-sm text-gray-600">
                            {{
                                [
                                    selectedPoint.dyrektor_imie,
                                    selectedPoint.dyrektor_nazwisko,
                                ]
                                    .filter(Boolean)
                                    .join(" ")
                            }}
                        </div>
                    </div>

                    <!-- Student Count -->
                    <div
                        v-if="selectedPoint.liczba_uczniow"
                        class="bg-blue-50 rounded-lg p-4">
                        <h3 class="text-sm font-medium text-gray-700 mb-2">
                            Liczba uczniów
                        </h3>
                        <div class="text-sm text-gray-600">
                            {{ selectedPoint.liczba_uczniow }}
                        </div>
                    </div>

                    <!-- Address Details -->
                    <div class="bg-blue-50 rounded-lg p-4">
                        <h3 class="text-sm font-medium text-gray-700 mb-2">
                            Adres
                        </h3>
                        <div class="text-sm text-gray-600 space-y-1">
                            <div v-if="selectedPoint.numer_budynku">
                                <span class="font-medium">Numer budynku:</span>
                                {{ selectedPoint.numer_budynku }}
                            </div>
                            <div v-if="selectedPoint.numer_lokalu">
                                <span class="font-medium">Numer lokalu:</span>
                                {{ selectedPoint.numer_lokalu }}
                            </div>
                        </div>
                    </div>

                    <!-- Website -->
                    <div
                        v-if="selectedPoint.strona_internetowa"
                        class="bg-blue-50 rounded-lg p-4">
                        <h3 class="text-sm font-medium text-gray-700 mb-2">
                            Strona internetowa
                        </h3>
                        <div class="text-sm">
                            <a
                                :href="selectedPoint.strona_internetowa"
                                target="_blank"
                                rel="noopener noreferrer"
                                class="text-blue-600 hover:underline break-words">
                                {{ selectedPoint.strona_internetowa }}
                            </a>
                        </div>
                    </div>

                    <!-- Administrative Information -->
                    <div class="bg-blue-50 rounded-lg p-4">
                        <h3 class="text-sm font-medium text-gray-700 mb-2">
                            Informacje administracyjne
                        </h3>
                        <div class="text-sm text-gray-600 space-y-1">
                            <div v-if="selectedPoint.regon">
                                <span class="font-medium">REGON:</span>
                                {{ selectedPoint.regon }}
                            </div>
                            <div v-if="selectedPoint.nip">
                                <span class="font-medium">NIP:</span>
                                {{ selectedPoint.nip }}
                            </div>
                            <div>
                                <span class="font-medium">ID:</span>
                                {{ selectedPoint.id }}
                            </div>
                        </div>
                    </div>
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
