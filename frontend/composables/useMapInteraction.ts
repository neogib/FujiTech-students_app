import type { Point } from "geojson"
import type { LngLatBounds } from "maplibre-gl"
import maplibregl from "maplibre-gl"
import type { MapMouseLayerEvent } from "~/types/map"
import type { SzkolaPublic, SzkolaPublicShort } from "~/types/schools"

export const useMapInteractions = (
    emit: (event: "point-clicked", school: SzkolaPublic) => void,
    updateQueryBboxParam: (bounds: LngLatBounds) => void,
) => {
    const popup = new maplibregl.Popup({
        closeButton: false,
        closeOnClick: false,
    })

    let currentFeatureCoordinates: string | undefined = undefined
    let debounceTimeout: NodeJS.Timeout | null = null

    const handleMouseMove = (map: maplibregl.Map, e: MapMouseLayerEvent) => {
        const feature_collection = e.features?.[0]
        if (!feature_collection) return

        const pointGeometry = feature_collection.geometry as Point
        const featureCoordinates = pointGeometry.coordinates.toString()
        if (currentFeatureCoordinates !== featureCoordinates) {
            currentFeatureCoordinates = featureCoordinates

            // Change the cursor style as a UI indicator.
            map.getCanvas().style.cursor = "pointer"

            const coordinates = pointGeometry.coordinates.slice() as [
                number,
                number,
            ]
            const feature_properties: SzkolaPublicShort =
                feature_collection.properties as SzkolaPublicShort
            // TODO: customize popup content
            const description = `${feature_properties.nazwa} ${feature_properties.numer_rspo} ${feature_properties.geolokalizacja_latitude} ${feature_properties.geolokalizacja_longitude} score: ${feature_properties.score}`

            // Ensure that if the map is zoomed out such that multiple
            // copies of the feature are visible, the popup appears
            // over the copy being pointed to.
            while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360
            }

            // Populate the popup and set its coordinates
            // based on the feature found.
            popup.setLngLat(coordinates).setHTML(description).addTo(map)
        }
    }

    const handleMouseLeave = (map: maplibregl.Map) => {
        currentFeatureCoordinates = undefined
        map.getCanvas().style.cursor = ""
        popup.remove()
    }

    const handleClick = async (e: MapMouseLayerEvent) => {
        const feature_collection = e.features?.[0]
        if (!feature_collection) return

        const schoolFullDetails = await useApi<SzkolaPublic>(
            `/schools/${feature_collection.properties.id}`,
        )

        if (schoolFullDetails.data.value) {
            emit("point-clicked", schoolFullDetails.data.value)
        }
    }

    const handleClusterClick = async (
        map: maplibregl.Map,
        e: MapMouseLayerEvent,
    ) => {
        const features = map.queryRenderedFeatures(e.point, {
            layers: ["clusters"],
        })
        const clusterId = features[0]?.properties.cluster_id
        const zoom = await map
            .getSource("schools-source")
            ?.getClusterExpansionZoom(clusterId)
        map.easeTo({
            center: features[0].geometry.coordinates,
            zoom,
        })
    }

    const handleMoveEnd = (map: maplibregl.Map) => {
        // Clear the previous timeout if it exists
        if (debounceTimeout) {
            clearTimeout(debounceTimeout)
        }

        // Set a new timeout
        debounceTimeout = setTimeout(() => {
            updateQueryBboxParam(map.getBounds())
        }, 300) // Wait for 300ms of inactivity before fetching
    }

    const setupMapEventHandlers = (map: maplibregl.Map) => {
        map.on("mousemove", "unclustered-points", (e) =>
            handleMouseMove(map, e),
        )
        map.on("mouseleave", "unclustered-points", () => handleMouseLeave(map))
        map.on("click", "unclustered-points", handleClick)
        map.on("click", "clusters", (e) => handleClusterClick(map, e))
        map.on("moveend", () => handleMoveEnd(map))
    }

    return { setupMapEventHandlers }
}
