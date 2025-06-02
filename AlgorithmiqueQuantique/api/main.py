import os
from typing import Callable, Dict, List

import toml
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from api.challenges import (
    challenge_1,
    challenge_2,
    challenge_grover_1,
    challenge_grover_2,
)

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
config = toml.load(DIR_PATH + "/config.toml")

app = FastAPI()
challenges: Dict[int, Callable] = {1: challenge_1, 2: challenge_2}


@app.get("/healthcheck")
async def healthcheck() -> JSONResponse:
    return JSONResponse(content={"message": "Statut : en pleine forme !"})


@app.post("/challenges/{challenge_id}")
async def challenge(
    challenge_id: int,
    data: Dict[str, List[float]],
) -> JSONResponse:
    result = challenges[challenge_id](data)
    if result[0]:
        message = f"GG ! Voici le drapeau : {config['flags'][str(challenge_id)]}"
    else:
        message = f"Raté !\n\n{result[1]}"
    return JSONResponse(content={"message": message})


@app.post("/grover/{grover_id}")
async def grover(
    grover_id: int,
    data: Dict[str, List[float] | List[int]],
) -> JSONResponse:
    if grover_id == 1:
        message = challenge_grover_1(data)
    else:
        message = challenge_grover_2(data)
    return JSONResponse(content={"message": message})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
