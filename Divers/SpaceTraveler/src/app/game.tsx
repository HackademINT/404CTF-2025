import React, {useState, useEffect} from 'react';
import './game.css';
import Asteroid, {AsteroidData} from "@/app/asteroid";
import Player from "@/app/player";
import {asteroidSize, clamp, playerSize, SpawnAsteroid} from "../../utils";

interface AsteroidWave {
    x: number;
    speed: number;
    index: number;
    completed: boolean;
}

interface WaveData {
    event: string;
    i: number;
    time: number;
    spawns: SpawnAsteroid[];
}

interface RewardData {
    flag: string;
}

// Huge inspiration from https://www.geeksforgeeks.org/flappy-bird-game-using-react-js/
const Game = ({eventTarget, sendPacket, sendPacketWithData}: {
    eventTarget: EventTarget,
    sendPacket: (type: string) => void,
    sendPacketWithData: (...data: string[]) => void
}) => {
    const [playerPosition, setPlayerPosition] = useState({x: 50, y: 200});
    const [asteroids, setAsteroids] = useState<AsteroidData[]>([]);
    const [waves, setWaves] = useState<AsteroidWave[]>([]);
    const [gameOver, setGameOver] = useState(false);
    const [score, setScore] = useState(0);
    const [gameStarted, setGameStarted] = useState(false);
    const [flag, setFlag] = useState("");

    const onClick = () => {
        if (!gameOver && !gameStarted) {
            // Start the game on the first jump
            setGameStarted(true);
            setScore(0);
            sendPacket("game_start");
        } else if (gameOver && !gameStarted) {
            // Restart the game
            setPlayerPosition({x: 50, y: 200});
            setAsteroids([]);
            setWaves([]);
            setGameOver(false);
            setGameStarted(true);
            setScore(0);
            sendPacket("game_start");
        }
    }

    const moveUp = () => {
        // Check if bird is out of the screen vertically
        setPlayerPosition(prev => ({x: 50, y: clamp(prev.y - 20, 0, 560)}));
    };

    const moveDown = () => {
        // Check if bird is out of the screen vertically
        setPlayerPosition(prev => ({x: 50, y: clamp(prev.y + 20, 0, 560)}));
    };

    const checkCollision = () => {
        const top = playerPosition.y;
        const left = playerPosition.x;

        asteroids.forEach((asteroid) => {
            const asteroidTop = asteroid.y;
            const asteroidLeft = asteroid.x;

            if (asteroidLeft < left + playerSize.width &&
                asteroidLeft + asteroidSize.width > left &&
                asteroidTop < top + playerSize.height &&
                asteroidSize.height + asteroidTop > top) {
                loseGame(true);
            }
        });
    }

    useEffect(() => {
        checkCollision();
    }, [playerPosition, asteroids, gameOver]);

    useEffect(() => {
        const pipeMove = setInterval(() => {
            if (!gameOver && gameStarted) {
                setAsteroids((prev) =>
                    prev.map((asteroid) => ({...asteroid, x: asteroid.x - asteroid.speed}))
                );
                setAsteroids(prev => prev.filter(asteroid => asteroid.x >= -asteroidSize.width * asteroid.speed));
                setWaves(prev => prev.map(wave => ({...wave, x: wave.x - wave.speed})))
                setWaves(prev => prev.filter(wave => !wave.completed));
            }
        }, 30);

        return () => {
            clearInterval(pipeMove);
        };
    }, [gameOver, gameStarted]);

    useEffect(() => {
        for (const wave of waves) {
            if (wave.completed) {
                continue;
            }
            if (wave.x < playerPosition.x - playerSize.width / 2 - asteroidSize.width / 2) {
                wave.completed = true;

                sendPacketWithData("wave_completed", JSON.stringify({
                    playerY: playerPosition.y,
                    waveIndex: wave.index
                }));
            }
        }
    }, [waves]);

    function keybindHandler(e: KeyboardEvent) {
        switch (e.key) {
            case "z":
                moveUp();
                break;
            case "s":
                moveDown();
                break;
        }
    }

    // Keybindings
    useEffect(() => {
        if (!gameStarted) {
            return;
        }

        document.addEventListener("keydown", keybindHandler);

        return () => {
            document.removeEventListener("keydown", keybindHandler);
        }
    }, [gameStarted]);


    function spawnAsteroid(waveEvent: CustomEventInit<WaveData>) {
        if (!waveEvent.detail) {
            return;
        }
        const detail = waveEvent.detail;

        const newAsteroids: AsteroidData[] = [];
        for (const position of detail.spawns) {
            newAsteroids.push({x: 400, y: position.y, speed: position.speed});
        }

        setAsteroids((prevAsteroid) => [...prevAsteroid, ...newAsteroids])
        setWaves(prevWaves => [...prevWaves, {
            x: 400,
            index: detail.i,
            speed: detail.spawns[0].speed,
            completed: false
        }]);
    }

    function loseGame(fromClient: boolean) {
        if (fromClient && !gameOver) {
            sendPacket("game_over");
        }
        setGameOver(true);
        setGameStarted(false);
    }

    function scoreUp() {
        setScore(prev => prev + 1);
    }

    function rewarded(rewardEvent: CustomEventInit<RewardData>) {
        if (!rewardEvent.detail) {
            return;
        }
        setFlag(rewardEvent.detail.flag);
    }

    // Spawning waves
    useEffect(() => {
        eventTarget.addEventListener("wave", spawnAsteroid);
        eventTarget.addEventListener("score_up", scoreUp);
        eventTarget.addEventListener("game_over", () => loseGame(false));
        eventTarget.addEventListener("reward", rewarded);
    }, []);

    return (
        <div className={`Game ${gameOver ? 'game-over' : ''}`} onClick={onClick}>
            <Player position={playerPosition} size={playerSize}/>
            {asteroids.map((asteroid, index) => (
                <Asteroid key={index} position={asteroid}/>
            ))}

            <center>
                <div className="score">{score}</div>
                <div className="flag">{flag}</div>
            </center>

            {gameOver && (
                <center>
                    <div className="game-over-message">
                        Game Over!
                        <br/>
                        Z to go UP, S to go DOWN
                        <br/>
                        <p style={{backgroundColor: 'blue', padding: "2px 6px", borderRadius: '5px'}}>
                            Click anywhere to Restart
                        </p>
                    </div>
                </center>
            )}

            {!gameStarted && !gameOver && (
                <center>
                    <div className="game-over-message">
                        Space explorer
                        <br/>
                        Z to go UP, S to go DOWN
                        <br/>
                        <p style={{backgroundColor: 'blue', padding: "2px 6px", borderRadius: '5px'}}>
                            Click anywhere to Start
                        </p>
                    </div>
                </center>
            )}
        </div>
    );
};

export default Game;
