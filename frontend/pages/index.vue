<script setup lang="ts">
import { ref } from "vue";
// import VoivodeshipsMap from "~/components/VoivodeshipsMap.vue";
import { voivodeshipNames } from "~/data/voivodeships";
// import NavBar from "~/components/NavBar.vue";

// State to manage mobile menu visibility
const isMobileMenuOpen = ref(false);

// Define reactive data for form
const selectedSchoolType = ref<string>("");
const selectedVoivodeship = ref<string>("");

// School types available in Polish
const schoolTypes = [
    { value: "przedszkole", label: "Przedszkole" },
    { value: "szkola-podstawowa", label: "Szkoła podstawowa" },
    { value: "liceum", label: "Liceum" },
    { value: "technikum", label: "Technikum" },
];

/**
 * Handle voivodeship selection from the map
 * @param voivodeshipId - ID of the selected voivodeship
 */
const handleVoivodeshipSelect = (voivodeshipId: string) => {
    selectedVoivodeship.value = voivodeshipId;
};

/**
 * Handle form submission
 */
const handleSubmit = () => {
    if (!selectedSchoolType.value || !selectedVoivodeship.value) {
        alert("Proszę wybrać typ szkoły i województwo");
        return;
    }

    // Log the selections to console as requested
    console.log("Typ szkoły:", selectedSchoolType.value);
    console.log("Województwo:", selectedVoivodeship.value);

    // Here would be the redirect to map page in the future
    console.log("Przekierowanie do strony mapy...");
};

/**
 * Reset form selections
 */
const resetForm = () => {
    selectedSchoolType.value = "";
    selectedVoivodeship.value = "";
};
</script>

<template>
    <div
        class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
        <!-- Navigation Bar -->
        <NavBar @toggle-menu="isMobileMenuOpen = !isMobileMenuOpen" />

        <!-- Main Content -->
        <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <!-- Hero Section -->
            <div class="text-center mb-12">
                <h1 class="text-4xl md:text-6xl font-bold text-gray-900 mb-4">
                    Ranking
                    <span class="text-indigo-600">Szkół</span>
                    w Polsce
                </h1>
                <p
                    class="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
                    Znajdź najlepsze szkoły w swojej okolicy. Porównuj wyniki,
                    sprawdzaj rankingi i podejmuj świadome decyzje edukacyjne
                    dla swojego dziecka.
                </p>
            </div>

            <!-- Main Content Grid -->
            <div class="grid lg:grid-cols-2 gap-12 items-start">
                <!-- Form Section -->
                <div
                    class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
                    <div class="mb-8">
                        <h2 class="text-2xl font-bold text-gray-900 mb-2">
                            Wybierz parametry wyszukiwania
                        </h2>
                        <p class="text-gray-600">
                            Zacznij od wyboru typu szkoły i województwa na mapie
                        </p>
                    </div>

                    <form class="space-y-6" @submit.prevent="handleSubmit">
                        <!-- School Type Selection -->
                        <div>
                            <label
                                for="school-type"
                                class="block text-sm font-medium text-gray-700 mb-3">
                                Typ szkoły *
                            </label>
                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div
                                    v-for="schoolType in schoolTypes"
                                    :key="schoolType.value"
                                    class="relative">
                                    <input
                                        :id="schoolType.value"
                                        v-model="selectedSchoolType"
                                        :value="schoolType.value"
                                        type="radio"
                                        name="school-type"
                                        class="peer sr-only" />
                                    <label
                                        :for="schoolType.value"
                                        class="block w-full p-4 text-center border-2 border-gray-200 rounded-lg cursor-pointer hover:border-indigo-300 peer-checked:border-indigo-500 peer-checked:bg-indigo-50 peer-checked:text-indigo-700 transition-all duration-200">
                                        <span class="font-medium">{{
                                            schoolType.label
                                        }}</span>
                                    </label>
                                </div>
                            </div>
                        </div>

                        <!-- Selected Voivodeship Display -->
                        <div>
                            <label
                                class="block text-sm font-medium text-gray-700 mb-3">
                                Wybrane województwo *
                            </label>
                            <div
                                class="p-4 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                                <div
                                    v-if="selectedVoivodeship"
                                    class="flex items-center justify-between">
                                    <span
                                        class="text-lg font-medium text-indigo-600">
                                        {{
                                            voivodeshipNames[
                                                selectedVoivodeship
                                            ]
                                        }}
                                    </span>
                                    <button
                                        type="button"
                                        class="text-red-500 hover:text-red-700 transition-colors"
                                        @click="selectedVoivodeship = ''">
                                        <svg
                                            class="h-5 w-5"
                                            fill="none"
                                            viewBox="0 0 24 24"
                                            stroke="currentColor">
                                            <path
                                                stroke-linecap="round"
                                                stroke-linejoin="round"
                                                stroke-width="2"
                                                d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>
                                <div
                                    v-else
                                    class="text-gray-500 text-center py-2">
                                    Kliknij na województwo na mapie →
                                </div>
                            </div>
                        </div>

                        <!-- Action Buttons -->
                        <div class="flex flex-col sm:flex-row gap-4 pt-6">
                            <button
                                type="submit"
                                :disabled="
                                    !selectedSchoolType || !selectedVoivodeship
                                "
                                class="flex-1 bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 active:scale-95">
                                Szukaj szkół
                            </button>
                            <button
                                type="button"
                                class="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200"
                                @click="resetForm">
                                Wyczyść
                            </button>
                        </div>
                    </form>
                </div>

                <!-- Map Section -->
                <div
                    class="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
                    <div class="mb-6">
                        <h2 class="text-2xl font-bold text-gray-900 mb-2">
                            Mapa województw
                        </h2>
                        <p class="text-gray-600">
                            Kliknij na województwo, aby je wybrać
                        </p>
                    </div>

                    <div class="relative">
                        <VoivodeshipsMap
                            @path-click="handleVoivodeshipSelect" />

                        <!-- Map overlay for selected voivodeship -->
                        <div
                            v-if="selectedVoivodeship"
                            class="absolute top-4 right-4 bg-indigo-100 text-indigo-800 px-3 py-2 rounded-lg text-sm font-medium border border-indigo-200">
                            Wybrano: {{ voivodeshipNames[selectedVoivodeship] }}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Additional Info Section -->
            <div
                class="mt-16 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-white">
                <div class="text-center">
                    <h2 class="text-3xl font-bold mb-4">
                        Dlaczego warto korzystać z naszego rankingu?
                    </h2>
                    <div class="grid md:grid-cols-3 gap-8 mt-8">
                        <div class="text-center">
                            <div
                                class="bg-white bg-opacity-20 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                                <svg
                                    class="h-8 w-8"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor">
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                </svg>
                            </div>
                            <h3 class="text-xl font-semibold mb-2">
                                Aktualne dane
                            </h3>
                            <p class="text-indigo-100">
                                Regularnie aktualizowane wyniki i statystyki
                                szkół
                            </p>
                        </div>
                        <div class="text-center">
                            <div
                                class="bg-white bg-opacity-20 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                                <svg
                                    class="h-8 w-8"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor">
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                            </div>
                            <h3 class="text-xl font-semibold mb-2">
                                Lokalizacja
                            </h3>
                            <p class="text-indigo-100">
                                Znajdź szkoły w swojej okolicy na interaktywnej
                                mapie
                            </p>
                        </div>
                        <div class="text-center">
                            <div
                                class="bg-white bg-opacity-20 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                                <svg
                                    class="h-8 w-8"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor">
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                                </svg>
                            </div>
                            <h3 class="text-xl font-semibold mb-2">
                                Łatwa porównywarka
                            </h3>
                            <p class="text-indigo-100">
                                Porównuj szkoły według różnych kryteriów
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <!-- Footer -->
        <footer class="bg-gray-900 text-white mt-16">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div class="text-center">
                    <h3 class="text-2xl font-bold mb-4">Ranking Szkół</h3>
                    <p class="text-gray-400 mb-8">
                        Najlepsze narzędzie do znajdowania szkół w Polsce
                    </p>
                    <div class="flex justify-center space-x-8">
                        <a
                            href="#"
                            class="text-gray-400 hover:text-white transition-colors"
                            >O nas</a
                        >
                        <a
                            href="#"
                            class="text-gray-400 hover:text-white transition-colors"
                            >Kontakt</a
                        >
                        <a
                            href="#"
                            class="text-gray-400 hover:text-white transition-colors"
                            >Polityka prywatności</a
                        >
                    </div>
                </div>
            </div>
        </footer>
    </div>
</template>
