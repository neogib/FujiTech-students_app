// Voivodeships mapping file
// Export a constant containing mappings of voivodeship keys to their respective names and bounding boxes
// later on we can use nominatim API from openstreetmap to get this data

/**
 * Coordinate pair representing latitude and longitude
 */
export interface View {
    south: number
    north: number
    west: number
    east: number
}

/**
 * Voivodeship data structure containing name and bounding box coordinates
 */
export interface VoivodeshipData {
    name: string
    coordinates: View
}

/**
 * Mapping of voivodeship keys to their respective data including Polish names and bounding boxes
 * Bounding boxes are approximate extents derived from Wikipedia's location map definitions
 */
export const voivodeshipNames: Record<string, VoivodeshipData> = {
    dolnoslaskie: {
        name: "Dolnośląskie",
        coordinates: {
            north: 51.9134,
            south: 49.9809,
            west: 14.7603,
            east: 17.9091,
        },
    },
    kujawsko_pomorskie: {
        name: "Kujawsko-pomorskie",
        coordinates: { north: 53.83, south: 52.28, west: 17.16, east: 19.88 },
    },
    lubelskie: {
        name: "Lubelskie",
        coordinates: { north: 52.35, south: 50.2, west: 21.52, east: 24.25 },
    },
    lubuskie: {
        name: "Lubuskie",
        coordinates: { north: 53.18, south: 51.33, west: 14.4, east: 16.6 },
    },
    lodzkie: {
        name: "Łódzkie",
        coordinates: { north: 52.45, south: 50.78, west: 17.95, east: 20.75 },
    },
    malopolskie: {
        name: "Małopolskie",
        coordinates: { north: 50.59, south: 49.07, west: 18.92, east: 21.55 },
    },
    mazowieckie: {
        name: "Mazowieckie",
        coordinates: { north: 53.55, south: 50.95, west: 19.15, east: 23.25 },
    },
    opolskie: {
        name: "Opolskie",
        coordinates: {
            north: 51.2778,
            south: 49.942,
            west: 16.8461,
            east: 18.8073,
        },
    },
    podkarpackie: {
        name: "Podkarpackie",
        coordinates: { north: 50.9, south: 48.95, west: 21.03, east: 23.66 },
    },
    podlaskie: {
        name: "Podlaskie",
        coordinates: { north: 54.5, south: 52.17, west: 21.45, east: 24.1 },
    },
    pomorskie: {
        name: "Pomorskie",
        coordinates: { north: 54.92, south: 53.4, west: 16.65, east: 19.75 },
    },
    slaskie: {
        name: "Śląskie",
        coordinates: {
            north: 51.1617,
            south: 49.2956,
            west: 17.8872,
            east: 20.0559,
        },
    },
    swietokrzyskie: {
        name: "Świętokrzyskie",
        coordinates: { north: 51.4, south: 50.1, west: 19.6, east: 22.0 },
    },
    "warminsko-mazurskie": {
        name: "Warmińsko-mazurskie",
        coordinates: { north: 54.52, south: 53.07, west: 19.05, east: 22.95 },
    },
    wielkopolskie: {
        name: "Wielkopolskie",
        coordinates: { north: 53.7, south: 51.05, west: 15.68, east: 19.19 },
    },
    "zachodnio-pomorskie": {
        name: "Zachodniopomorskie",
        coordinates: { north: 54.65, south: 52.58, west: 13.95, east: 17.1 },
    },
}
