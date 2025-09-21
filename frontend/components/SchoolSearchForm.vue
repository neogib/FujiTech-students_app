<script setup lang="ts">
import { ref, computed } from "vue"
import { voivodeshipNames } from "~/data/voivodeships"

const props = defineProps<{
    readonly selectedVoivodeship: string
}>()

const emit = defineEmits<{
    (e: "submit", payload: { schoolType: string; voivodeship: string }): void
    (e: "clear-voivodeship"): void
}>()

const selectedSchoolType = ref<string>("")

const schoolTypes = [
    { value: "przedszkole", label: "Przedszkole" },
    { value: "szkola-podstawowa", label: "Szkoła podstawowa" },
    { value: "liceum", label: "Liceum" },
    { value: "technikum", label: "Technikum" },
]

const voivodeshipName = computed(() => {
    return props.selectedVoivodeship
        ? voivodeshipNames[props.selectedVoivodeship]
        : ""
})

const handleSubmit = () => {
    if (!selectedSchoolType.value || !props.selectedVoivodeship) {
        alert("Proszę wybrać typ szkoły i województwo")
        return
    }
    // Emit the submit event with the form data as a payload
    emit("submit", {
        schoolType: selectedSchoolType.value,
        voivodeship: props.selectedVoivodeship,
    })
}

const resetForm = () => {
    selectedSchoolType.value = ""
    // We also need to tell the parent to clear its state
    emit("clear-voivodeship")
}
</script>

<template>
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
                <label class="block text-sm font-medium text-gray-700 mb-3">
                    Wybrane województwo *
                </label>
                <div
                    class="p-4 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                    <div
                        v-if="selectedVoivodeship"
                        class="flex justify-between">
                        <span class="text-lg font-medium text-indigo-600">
                            {{ voivodeshipName }}
                        </span>
                        <button
                            type="button"
                            class="text-red-500 hover:text-red-700 transition-colors"
                            @click="emit('clear-voivodeship')">
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
                    <div v-else class="text-gray-500 text-center py-2">
                        Kliknij na województwo na mapie →
                    </div>
                </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex flex-col sm:flex-row gap-4 pt-6">
                <button
                    type="submit"
                    :disabled="!selectedSchoolType || !selectedVoivodeship"
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
</template>

<style scoped>
@reference "tailwindcss";

.form-button {
    @apply px-6 py-3 border border-gray-300  rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200;
}
</style>
