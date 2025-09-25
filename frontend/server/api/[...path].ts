import { defineEventHandler, getRequestURL, proxyRequest } from "h3"

export default defineEventHandler(async (event) => {
    // Rewrite /api/foo -> <INTERNAL_API_BASE>/foo
    // console.log("API proxy handler invoked", event)
    const url = getRequestURL(event)
    const base = process.env.NUXT_INTERNAL_API_BASE || "http://backend:8000"
    const target = base + url.pathname.replace(/^\/api/, "") + url.search
    return proxyRequest(event, target)
})
