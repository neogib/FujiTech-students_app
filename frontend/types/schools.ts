/**
 * TypeScript interfaces for school-related data models
 * These interfaces correspond to the backend Python models in app.models.schools
 */

export interface SchoolType {
    id: number
    nazwa: string
}

export interface PublicLegalStatus {
    id: number
    nazwa: string
}

/*
Used for displaying basic school information with location and ranking
Corresponds to backend SzkolaPublicShort model
 */
export interface SchoolShort {
    /** Unique identifier */
    id: number
    numer_rspo: number
    nazwa: string
    geolokalizacja_latitude: number
    geolokalizacja_longitude: number
    score: number
    typ: SchoolType
    status_publicznoprawny: PublicLegalStatus
}
