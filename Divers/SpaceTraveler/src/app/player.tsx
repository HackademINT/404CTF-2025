import React from "react";

const Player = ({position, size}: { position: { x: number, y: number }, size: { width: number, height: number } }) => {
    return (
        <img
            src="/images/player.png"
            alt="player"
            className="player"
            style={{
                left: position.x,
                top: position.y,
                width: `${size.width}px`,
                height: `${size.height}px`,
            }}
            draggable={true}
        />
    );
};

export default Player;