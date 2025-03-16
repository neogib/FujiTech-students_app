import { useRuntimeConfig } from "nuxt/app";

export function useApi<T>(endpoint: string, options = {}) {
  const config = useRuntimeConfig();
  return useFetch<T>(`${config.public.apiBase}${endpoint}`, {
    ...options,
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
}
