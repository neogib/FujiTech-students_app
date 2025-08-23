import { defineNuxtConfig } from "nuxt/config";
// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    compatibilityDate: "2025-08-23",
    devtools: { enabled: true },

    // Runtime environment configuration
    runtimeConfig: {
        public: {
            apiBase:
                process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000",
        },
    },

    modules: ["@nuxt/eslint"],
});
