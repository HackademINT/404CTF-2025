import React from "react";

export interface AsteroidData {
    x: number;
    y: number;
    speed: number;
}

const Asteroid = ({position}: { position: { x: number, y: number } }) => {
    return (
        <img
            src="/images/asteroid.png"
            alt="asteroid"
            className="asteroid"
            style={{
                left: position.x,
                top: position.y,
            }}
            draggable={true}
        />
    );
};

export default Asteroid;
