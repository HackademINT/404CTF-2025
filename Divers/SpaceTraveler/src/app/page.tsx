"use client";

import {useEffect} from "react";
import {socket} from "@/utils/socket";
import Game from "@/app/game";

export default function Home() {
    const eventTarget = new EventTarget();

    useEffect(() => {
        socket.on("message", (...args) => {
            if (args.length == 0) {
                return;
            }

            const msgType = args.shift();

            switch (msgType) {
                case "ping":
                    socket.send("pong");
                    break;
                case "message":
                    const data = JSON.parse(args[0]);

                    switch (data.event) {
                        case "new_wave":
                            eventTarget.dispatchEvent(new CustomEvent("wave", {detail: data}));
                            break;
                        case "game_over":
                            eventTarget.dispatchEvent(new CustomEvent("game_over"));
                            break;
                        case "score_up":
                            eventTarget.dispatchEvent(new CustomEvent("score_up"));
                            break;
                        case "reward":
                            eventTarget.dispatchEvent(new CustomEvent("reward", {detail: data}));
                            break;
                    }
                    break;
            }
        });

        return () => {
            socket.off("message");
        };
    }, []);

    function sendPacket(type: string) {
        socket.send(type);
    }

    function sendPacketWithData(type: string, data: string) {
        socket.send(type, data);
    }

    return <Game eventTarget={eventTarget} sendPacket={sendPacket} sendPacketWithData={sendPacketWithData}/>;
}