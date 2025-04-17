// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2024-11-01", // Keep this or update as needed
  devtools: {
    enabled: true,
    timeline: {
      enabled: true,
    },
  },
  css: [
    'maplibre-gl/dist/maplibre-gl.css' // Good - keep this
  ],
  // plugins: [ <--- REMOVE THIS ARRAY ENTIRELY
  //   '~/plugins/vue-maplibre-gl.ts'
  // ],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000",
    },
  },
  // Add this build option if you still encounter issues with the map library
  // build: {
  //   transpile: ['vue-maplibre-gl', 'maplibre-gl']
  // }
});