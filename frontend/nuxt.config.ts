// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2024-11-01",
  devtools: {
    enabled: true,
    timeline: {
      enabled: true,
    },
  },
  css: [
    'maplibre-gl/dist/maplibre-gl.css' // Dodano globalne style dla Maplibre
  ],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000",
      apiRspo: process.env.NUXT_PUBLIC_API_RSPO || "https://api-rspo.men.gov.pl/api",
    },
  },
});
