<script setup lang="ts">
import { ref } from "vue"
import { voivodeshipNames } from "~/data/voivodeships"

const isMobileMenuOpen = ref(false)

const selectedSchoolType = ref<string>("")
const selectedVoivodeship = ref<string>("")

// Available school types
const schoolTypes = [
    { value: "przedszkole", label: "Przedszkole" },
    { value: "szkola-podstawowa", label: "Szkoła podstawowa" },
    { value: "liceum", label: "Liceum" },
    { value: "technikum", label: "Technikum" },
]

const handleVoivodeshipSelect = (voivodeshipId: string) => {
    selectedVoivodeship.value = voivodeshipId
}

const handleSubmit = () => {
    if (!selectedSchoolType.value || !selectedVoivodeship.value) {
        alert("Proszę wybrać typ szkoły i województwo")
        return
    }

    console.log("Typ szkoły:", selectedSchoolType.value)
    console.log("Województwo:", selectedVoivodeship.value)

    // Here would be the redirect to map page in the future
    console.log("Przekierowanie do strony mapy...")
}

const resetForm = () => {
    selectedSchoolType.value = ""
    selectedVoivodeship.value = ""
}
</script>

<template>
    <div
        class="min-h-screen bg-linear-to-br from-blue-100 via-white to-indigo-200">
        <!-- Navigation Bar -->
        <NavBar @toggle-menu="isMobileMenuOpen = !isMobileMenuOpen" />

        <!-- Main Content -->
        <main class="max-w-7xl mx-auto px-2 sm:px-5 lg:px-8 py-8">
            <!-- Hero Section -->
            <div class="text-center mb-12">
                <h1 class="text-4xl md:text-6xl font-bold text-gray-900 mb-4">
                    Ranking
                    <span class="text-indigo-600">Szkół</span>
                    w Polsce
                </h1>
                <p class="text-xl text-gray-600 max-w-3xl mx-auto leading-8">
                    Znajdź najlepsze szkoły w swojej okolicy. Porównuj wyniki,
                    sprawdzaj rankingi i podejmuj świadome decyzje dotyczące
                    dalszej edukacji.
                </p>
            </div>

            <!-- Main Content Grid -->
            <div class="grid lg:grid-cols-2 gap-12 items-start">
                <!-- Form Section -->
                <div class="content-card">
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
                                    class="flex justify-between">
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
                                            class="w-5 h-5"
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
                                class="form-button bg-indigo-600 text-white hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed duration-200 hover:scale-105 active:scale-95">
                                Szukaj szkół
                            </button>
                            <button
                                type="button"
                                class="form-button text-gray-700 hover:bg-gray-50"
                                @click="resetForm">
                                Wyczyść
                            </button>
                        </div>
                    </form>
                </div>

                <!-- Map Section -->
                <div class="content-card">
                    <div class="mb-2">
                        <h2 class="text-2xl font-bold text-gray-900 mb-2">
                            Mapa województw
                        </h2>
                        <p class="text-gray-600">
                            Kliknij na województwo, aby je wybrać
                        </p>
                    </div>

                    <div class="relative p-2">
                        <VoivodeshipsMap
                            @path-click="handleVoivodeshipSelect" />

                        <!-- Map overlay for selected voivodeship -->
                        <div
                            v-if="selectedVoivodeship"
                            class="absolute top-0 right-0 bg-indigo-100 text-indigo-800 px-3 py-2 rounded-lg text-sm border border-indigo-200">
                            <p>
                                Wybrano:
                                {{ voivodeshipNames[selectedVoivodeship] }}
                            </p>
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
                            <img
                                src="~/assets/images/up-to-date_data.png"
                                alt="Aktualne dane"
                                class="feature-image" />
                            <h3 class="feature-heading">Aktualne dane</h3>
                            <p class="text-indigo-100">
                                Regularnie aktualizowane wyniki i statystyki
                                szkół
                            </p>
                        </div>
                        <div class="text-center">
                            <img
                                src="~/assets/images/location.png"
                                alt="Lokalizacja"
                                class="feature-image" />
                            <h3 class="feature-heading">Lokalizacja</h3>
                            <p class="text-indigo-100">
                                Znajdź szkoły w swojej okolicy na interaktywnej
                                mapie
                            </p>
                        </div>
                        <div class="text-center">
                            <img
                                src="~/assets/images/school_comparison.png"
                                alt="Łatwa porównywarka"
                                class="feature-image" />
                            <h3 class="feature-heading">Łatwa porównywarka</h3>
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
            <div
                class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 text-center">
                <h3 class="feature-heading">Ranking Szkół</h3>
                <p class="text-gray-400 mb-8">
                    Najlepsze narzędzie do znajdowania szkół w Polsce
                </p>
                <div class="flex flex-wrap justify-center gap-6 md:gap-8">
                    <a href="#" class="footer-nav-link">O nas</a>
                    <a href="#" class="footer-nav-link">Kontakt</a>
                    <a href="#" class="footer-nav-link">Polityka prywatności</a>
                </div>
            </div>
        </footer>
    </div>
</template>

<style scoped>
@import "tailwindcss";

.form-button {
    @apply px-6 py-3 border border-gray-300  rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200;
}

.content-card {
    @apply bg-white rounded-2xl shadow-xl p-4 md:p-6;
}

.feature-image {
    @apply w-24 h-24 rounded-full mb-4 mx-auto object-cover border-2 border-white/30;
}

.feature-heading {
    @apply text-xl font-semibold mb-2;
}

.footer-link {
    @apply text-gray-400 hover:text-white transition-colors;
}
</style>
