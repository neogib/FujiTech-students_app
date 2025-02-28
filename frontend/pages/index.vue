<script setup lang="ts">
import { useRuntimeConfig, useFetch } from "nuxt/app";

interface BackendResponse {
  message: string;
}

const config = useRuntimeConfig();
console.log("API Base:", config.public.apiBase);
const { data, error, pending } = useFetch<BackendResponse>(`/api/users`, {
  onRequest({ request, options }) {
    console.log("Starting Request:", request);
  },
  onResponse({ request, response, options }) {
    console.log("Response:", response._data);
  },
  onRequestError({ request, error, options }) {
    console.log("Request Error:", error);
  },
});
</script>

<template>
  <div>
    <h1>Test połączenia z backendem</h1>
    <div v-if="pending">Ładowanie...</div>
    <div v-else-if="error">Błąd: {{ error }}</div>
    <div v-else>
      <p>Odpowiedź z backendu: {{ data?.message }}</p>
    </div>
  </div>
</template>
