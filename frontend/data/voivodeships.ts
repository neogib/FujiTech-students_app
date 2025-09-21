// Voivodeships mapping file
// Export a constant containing mappings of voivodeship keys to their respective names and bounding boxes
// later on we can use nominatim API from openstreetmap to get this data

/**
 * Coordinate pair representing latitude and longitude
 */
export interface Coordinate {
    lat: number
    lon: number
}

/**
 * Voivodeship data structure containing name and bounding box coordinates
 */
export interface VoivodeshipData {
    name: string
    topLeft: Coordinate
    bottomRight: Coordinate
}

/**
 * Mapping of voivodeship keys to their respective data including Polish names and bounding boxes
 * Bounding boxes are approximate extents derived from Wikipedia's location map definitions
 */
export const voivodeshipNames: Record<string, VoivodeshipData> = {
    dolnoslaskie: {
        name: "Dolnośląskie",
        topLeft: { lat: 51.9134, lon: 14.7603 },
        bottomRight: { lat: 49.9809, lon: 17.9091 },
    },
    "kujawsko-pomorskie": {
        name: "Kujawsko-pomorskie",
        topLeft: { lat: 53.83, lon: 17.16 },
        bottomRight: { lat: 52.28, lon: 19.88 },
    },
    lubelskie: {
        name: "Lubelskie",
        topLeft: { lat: 52.35, lon: 21.52 },
        bottomRight: { lat: 50.2, lon: 24.25 },
    },
    lubuskie: {
        name: "Lubuskie",
        topLeft: { lat: 53.18, lon: 14.4 },
        bottomRight: { lat: 51.33, lon: 16.6 },
    },
    lodzkie: {
        name: "Łódzkie",
        topLeft: { lat: 52.45, lon: 17.95 },
        bottomRight: { lat: 50.78, lon: 20.75 },
    },
    malopolskie: {
        name: "Małopolskie",
        topLeft: { lat: 50.59, lon: 18.92 },
        bottomRight: { lat: 49.07, lon: 21.55 },
    },
    mazowieckie: {
        name: "Mazowieckie",
        topLeft: { lat: 53.55, lon: 19.15 },
        bottomRight: { lat: 50.95, lon: 23.25 },
    },
    opolskie: {
        name: "Opolskie",
        topLeft: { lat: 51.2778, lon: 16.8461 },
        bottomRight: { lat: 49.942, lon: 18.8073 },
    },
    podkarpackie: {
        name: "Podkarpackie",
        topLeft: { lat: 50.9, lon: 21.03 },
        bottomRight: { lat: 48.95, lon: 23.66 },
    },
    podlaskie: {
        name: "Podlaskie",
        topLeft: { lat: 54.5, lon: 21.45 },
        bottomRight: { lat: 52.17, lon: 24.1 },
    },
    pomorskie: {
        name: "Pomorskie",
        topLeft: { lat: 54.92, lon: 16.65 },
        bottomRight: { lat: 53.4, lon: 19.75 },
    },
    slaskie: {
        name: "Śląskie",
        topLeft: { lat: 51.1617, lon: 17.8872 },
        bottomRight: { lat: 49.2956, lon: 20.0559 },
    },
    swietokrzyskie: {
        name: "Świętokrzyskie",
        topLeft: { lat: 51.4, lon: 19.6 },
        bottomRight: { lat: 50.1, lon: 22.0 },
    },
    "warminsko-mazurskie": {
        name: "Warmińsko-mazurskie",
        topLeft: { lat: 54.52, lon: 19.05 },
        bottomRight: { lat: 53.07, lon: 22.95 },
    },
    wielkopolskie: {
        name: "Wielkopolskie",
        topLeft: { lat: 53.7, lon: 15.68 },
        bottomRight: { lat: 51.05, lon: 19.19 },
    },
    "zachodnio-pomorskie": {
        name: "Zachodniopomorskie",
        topLeft: { lat: 54.65, lon: 13.95 },
        bottomRight: { lat: 52.58, lon: 17.1 },
    },
}
