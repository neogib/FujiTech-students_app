<template>
    <img
        ref="triangle"
        src="~/assets/images/triangle.svg"
        alt="triangle"
        class="hidden" />
    <MglMap
        :map-style="style"
        :center="center"
        :zoom="zoom"
        height="100vh"
        @map:load="onMapLoaded">
        <MglNavigationControl />

        <mgl-image
            id="custom-marker"
            :image="triangle as HTMLImageElement"
            :options="{ sdf: true }" />

        <!-- Add your MglSource and MglLayer components here -->
        <MglGeoJsonSource source-id="my-data-source" :data="geoJsonSource">
            <MglSymbolLayer
                layer-id="my-interactive-layer"
                :paint="{
                    'icon-color': [
                        'interpolate',
                        ['linear'],
                        ['get', 'score'],
                        0,
                        '#FF0000', // red at 0
                        50,
                        '#FFFF00', // yellow at 50
                        100,
                        '#00FF00', // green at 100
                    ],
                }"
                :layout="{
                    'icon-image': 'custom-marker',
                    'icon-overlap': 'always',
                }" />
        </MglGeoJsonSource>
    </MglMap>
</template>

<script setup lang="ts">
import "maplibre-gl/dist/maplibre-gl.css";
import {
    MglMap,
    MglNavigationControl,
    MglGeoJsonSource,
    MglSymbolLayer,
} from "@indoorequal/vue-maplibre-gl";
import maplibregl from "maplibre-gl";

const triangle = useTemplateRef("triangle");
const popup = new maplibregl.Popup({
    closeButton: false,
    closeOnClick: false,
});

const style = "https://tiles.openfreemap.org/styles/liberty";
const center: [number, number] = [-77.04, 38.907];
const zoom = 11.15;

const onMapLoaded = (event: { map: maplibregl.Map }) => {
    let currentFeatureCoordinates: string | undefined = undefined;
    const map = event.map;
    map.on("mousemove", "my-interactive-layer", (e) => {
        const feature_collection = e.features?.[0];
        if (
            !feature_collection ||
            feature_collection.geometry.type !== "Point"
        ) {
            return;
        }

        // Type assertion since we've already checked that geometry.type is 'Point'
        const pointGeometry = feature_collection.geometry;
        const featureCoordinates = pointGeometry.coordinates.toString();
        if (currentFeatureCoordinates !== featureCoordinates) {
            currentFeatureCoordinates = featureCoordinates;

            // Change the cursor style as a UI indicator.
            map.getCanvas().style.cursor = "pointer";

            const coordinates = pointGeometry.coordinates.slice();
            const description = feature_collection.properties?.description;

            // Ensure that if the map is zoomed out such that multiple
            // copies of the feature are visible, the popup appears
            // over the copy being pointed to.
            while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
            }

            // Populate the popup and set its coordinates
            // based on the feature found.
            popup
                .setLngLat(coordinates as [number, number])
                .setHTML(description)
                .addTo(map);
        }
    });

    map.on("mouseleave", "my-interactive-layer", () => {
        currentFeatureCoordinates = undefined;
        map.getCanvas().style.cursor = "";
        popup.remove();
    });
};

const geoJsonSource = {
    type: "FeatureCollection",
    features: [
        {
            type: "Feature",
            properties: {
                description:
                    "<strong>Make it Mount Pleasant</strong><p>Make it Mount Pleasant is a handmade and vintage market and afternoon of live entertainment and kids activities. 12:00-6:00 p.m.</p>",
            },
            geometry: {
                type: "Point",
                coordinates: [-77.038659, 38.931567],
            },
        },
        {
            type: "Feature",
            properties: {
                score: 95,
                description:
                    "<strong>Mad Men Season Five Finale Watch Party</strong><p>Head to Lounge 201 (201 Massachusetts Avenue NE) Sunday for a Mad Men Season Five Finale Watch Party, complete with 60s costume contest, Mad Men trivia, and retro food and drink. 8:00-11:00 p.m. $10 general admission, $20 admission and two hour open bar.</p>",
            },
            geometry: {
                type: "Point",
                coordinates: [-77.003168, 38.894651],
            },
        },
        {
            type: "Feature",
            properties: {
                description:
                    "<strong>Big Backyard Beach Bash and Wine Fest</strong><p>EatBar (2761 Washington Boulevard Arlington VA) is throwing a Big Backyard Beach Bash and Wine Fest on Saturday, serving up conch fritters, fish tacos and crab sliders, and Red Apron hot dogs. 12:00-3:00 p.m. $25.</p>",
            },
            geometry: {
                type: "Point",
                coordinates: [-77.090372, 38.881189],
            },
        },
        {
            type: "Feature",
            properties: {
                description:
                    "<strong>Ballston Arts & Crafts Market</strong><p>The Ballston Arts & Crafts Market sets up shop next to the Ballston metro this Saturday for the first of five dates this summer. Nearly 35 artists and crafters will be on hand selling their wares. 10:00-4:00 p.m.</p>",
            },
            geometry: {
                type: "Point",
                coordinates: [-77.111561, 38.882342],
            },
        },
        {
            type: "Feature",
            properties: {
                description:
                    "<strong>Seersucker Bike Ride and Social</strong><p>Feeling dandy? Get fancy, grab your bike, and take part in this year's Seersucker Social bike ride from Dandies and Quaintrelles. After the ride enjoy a lawn party at Hillwood with jazz, cocktails, paper hat-making, and more. 11:00-7:00 p.m.</p>",
            },
            geometry: {
                type: "Point",
                coordinates: [-77.052477, 38.943951],
            },
        },
        {
            type: "Feature",
            properties: {
                description:
                    "<strong>Capital Pride Parade</strong><p>The annual Capital Pride Parade makes its way through Dupont this Saturday. 4:30 p.m. Free.</p>",
            },
            geometry: {
                type: "Point",
                coordinates: [-77.043444, 38.909664],
            },
        },
        {
            type: "Feature",
            properties: {
                description:
                    "<strong>Muhsinah</strong><p>Jazz-influenced hip hop artist Muhsinah plays the Black Cat (1811 14th Street NW) tonight with Exit Clov and Gods’illa. 9:00 p.m. $12.</p>",
            },
            geometry: {
                type: "Point",
                coordinates: [-77.031706, 38.914581],
            },
        },
        {
            type: "Feature",
            properties: {
                description:
                    "<strong>A Little Night Music</strong><p>The Arlington Players' production of Stephen Sondheim's <em>A Little Night Music</em> comes to the Kogod Cradle at The Mead Center for American Theater (1101 6th Street SW) this weekend and next. 8:00 p.m.</p>",
            },
            geometry: {
                type: "Point",
                coordinates: [-77.020945, 38.878241],
            },
        },
        {
            type: "Feature",
            properties: {
                description:
                    "<strong>Truckeroo</strong><p>Truckeroo brings dozens of food trucks, live music, and games to half and M Street SE (across from Navy Yard Metro Station) today from 11:00 a.m. to 11:00 p.m.</p>",
            },
            geometry: {
                type: "Point",
                coordinates: [-77.007481, 38.876516],
            },
        },
    ],
};
</script>
