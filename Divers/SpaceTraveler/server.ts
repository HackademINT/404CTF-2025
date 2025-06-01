import {parse} from "url";
import {DefaultEventsMap, Server, Socket} from "socket.io";
import next from "next";
import {createServer, IncomingMessage, ServerResponse} from "node:http";
import {clearInterval, clearTimeout, setInterval} from "node:timers";
import {asteroidSize, mapSize, playerSize, SpawnAsteroid} from "./utils";

const PORT = process.env.PORT || 3000;
const DEV = process.env.NODE_ENV !== 'production';
const FLAG = process.env.FLAG || "404CTF{TEST_FLAG}";

const app = next({dev: DEV});
const handle = app.getRequestHandler();

app.prepare().then(() => {
    const server = createServer((req: IncomingMessage, res: ServerResponse) => {
        handle(req, res, parse(req.url || "", true));
    });

    const io = new Server(server);

    io.on("connection", socket => {
        //console.log(`Connection received`);

        const playerRun = new PlayerRun(socket);

        socket.on("message", (...args) => {
            //console.log(`Received message: ${args.toString()}`)

            const msgType = args.shift();
            switch (msgType) {
                case "ping":
                    socket.send("pong");
                    break;
                case "game_start":
                    playerRun.reset();
                    playerRun.startSendingWaves();
                    break;
                case "game_over":
                    playerRun.stopSendingWaves();
                    break;
                case "wave_completed":
                    const data = JSON.parse(args[0]);
                    playerRun.testWave(data.playerY, data.waveIndex);
                    break;
            }
        });

        socket.on("close", () => {
            //console.log("Client disconnected");
            playerRun.stopSendingWaves();
        });
    });

    server.listen(PORT, () => {
        console.log(`Listening on http://localhost:${PORT}`);
    });
});

class PlayerRun {
    waveIndex: number;
    beginTime: number;
    score: number;
    asteroidSending: NodeJS.Timeout | null;
    socket: Socket;
    sentWaves: { [waveId: number]: { generatedSpawns: SpawnAsteroid[], timeout: NodeJS.Timeout } };
    latestSafePosition: number;

    /* eslint-disable  @typescript-eslint/no-explicit-any */
    constructor(socket: Socket<DefaultEventsMap, DefaultEventsMap, DefaultEventsMap, any>) {
        this.waveIndex = 0;
        this.beginTime = Date.now();
        this.score = 0;
        this.asteroidSending = null;
        this.socket = socket;
        this.sentWaves = {};
        this.latestSafePosition = 0;

        this.sendEvent("init");
    }

    sendEvent(event: string) {
        this.socket.send("message", JSON.stringify({event: event}));
    }

    reset() {
        this.waveIndex = 0;
        this.beginTime = Date.now();
        this.score = 0;

        for (const sentWave of Object.values(this.sentWaves)) {
            clearTimeout(sentWave.timeout);
        }
        this.sentWaves = {};
    }

    startSendingWaves() {
        this.stopSendingWaves();

        this.asteroidSending = setInterval(() => {
            const currentTime = Math.floor(0.001 * (Date.now() - this.beginTime));
            const generatedSpawns = generateWave(currentTime, this);

            const i = this.waveIndex;
            this.socket.send("message", JSON.stringify({
                event: "new_wave",
                i,
                time: currentTime,
                spawns: generatedSpawns
            }));
            this.waveIndex++;

            // Spawn at x=400, player is at x=50, d=350 pixels to travel at speed v=(asteroid.speed / 30ms)
            // t = d/v = d * 30 / asteroid.speed, we add 3000ms to account for latency and other sources of incoherence

            const maxTimeUntilTimeout = 3000 + 350 * 30 / generatedSpawns[0].speed;
            const timeout = setTimeout(() => {
                this.sendGameOver();
            }, maxTimeUntilTimeout);

            this.sentWaves[i] = {generatedSpawns, timeout};
        }, 1000);
    }

    stopSendingWaves() {
        if (this.asteroidSending) {
            clearInterval(this.asteroidSending);
        }
    }

    testWave(playerY: number, waveIndex: number) {
        if (!(waveIndex in this.sentWaves)) {
            this.sendGameOver();
            return;
        }

        if (playerY < 0 || playerY > mapSize.height - playerSize.height) {
            this.sendGameOver();
            return;
        }

        for (const spawn of this.sentWaves[waveIndex].generatedSpawns) {
            if (spawn.y < playerY + playerSize.height &&
                spawn.y + asteroidSize.height > playerY) {
                this.sendGameOver();
                return;
            }
        }

        clearTimeout(this.sentWaves[waveIndex].timeout);
        delete this.sentWaves[waveIndex];
        this.sendEvent("score_up");
        this.score++;

        if (this.score == 90) {
            this.socket.send("message", JSON.stringify({event: "reward", flag: FLAG}));
        }
    }

    sendGameOver() {
        this.stopSendingWaves();
        this.sendEvent("game_over");
        this.reset();
    }
}

function getAsteroidCount(currentTime: number) {
    if (currentTime >= 30) {
        return 9;
    }
    return 1 + 8 * currentTime / 30;
}

function generateSafePosition(instance: PlayerRun) {
    const value = Math.floor(Math.random() * (mapSize.height - 2 * playerSize.height));
    if (value <= instance.latestSafePosition) {
        return value;
    }
    return value + playerSize.height;
}

function generateWave(currentTime: number, instance: PlayerRun): SpawnAsteroid[] {
    const speed = 1 + 15 * Math.pow(Math.cos(2 * Math.PI * currentTime / 5), 2);//Math.log10(currentTime + 1);
    const asteroidCount = getAsteroidCount(currentTime);
    const wave: SpawnAsteroid[] = [];

    const playerSafePosBottom = generateSafePosition(instance);
    instance.latestSafePosition = playerSafePosBottom;
    const playerSafePosTop = playerSafePosBottom + playerSize.height;

    const ranges: { y1: number, y2: number, fromStart: boolean }[] = [];
    // Making the first spawn range from the bottom to the player safe zone
    const firstLimit = playerSafePosBottom - asteroidSize.height
    if (firstLimit > 0) {
        ranges.push({y1: 0, y2: firstLimit, fromStart: true});
    }

    // Making the second spawn range from the player safe zone to the top
    const secondLimit = mapSize.height - asteroidSize.height;
    if (playerSafePosTop < secondLimit) {
        ranges.push({y1: playerSafePosTop, y2: secondLimit, fromStart: false});
    }

    const availableSlots: number[] = [];

    // Listing the available slots
    for (const range of ranges) {
        const spawnCount = Math.floor((range.y2 - range.y1) / asteroidSize.height);

        for (let i = 0; i < spawnCount; i++) {
            if (range.fromStart) {
                availableSlots.push(range.y1 + i * asteroidSize.height);
            } else {
                availableSlots.push(range.y2 - i * asteroidSize.height);
            }
        }
    }

    const waveCount = Math.min(asteroidCount, availableSlots.length);
    // Making the wave with random slots
    for (let i = 0; i < waveCount; i++) {
        const index = Math.floor(Math.random() * availableSlots.length);
        wave.push({y: availableSlots[index], speed});
        availableSlots.splice(index, 1);
    }

    return wave;
}
