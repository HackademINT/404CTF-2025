export interface SpawnAsteroid {
    y: number;
    speed: number;
}

export const clamp = (val: number, min: number, max: number) => Math.min(Math.max(val, min), max);

export const playerSize = {width: 49, height: 40};
export const asteroidSize = {width: 55, height: 48};
export const mapSize = {width: 600, height: 600};