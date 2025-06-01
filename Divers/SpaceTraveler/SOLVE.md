# Solve
Voici une possibilité pour solve:

> requirements.txt
```
python-socketio[client]~=5.13.0
requests~=2.32.3
websocket-client~=1.8.0
```

> solve.py
```python
import socketio
import json

sio = socketio.Client()

player_height = 40
asteroid_height = 48

@sio.event
def connect():
	print('connection established, starting solve')
	sio.emit("message", "game_start")


def get_safe_pos(positions):
	ordered_positions = sorted(positions, key=lambda x: x["y"])

	if ordered_positions[0]["y"] > player_height:
		return 0

	for i in range(len(ordered_positions) - 1):
		pos1 = ordered_positions[i]
		pos2 = ordered_positions[i+1]
		if pos2["y"] - pos1["y"] > asteroid_height + player_height + 1:
			return pos2["y"] - (player_height + 1)

	if 600 - (ordered_positions[-1]["y"] + asteroid_height) > player_height + 1:
		return ordered_positions[-1]["y"] + asteroid_height + 1

	return 0

score = 0

@sio.event
def message(_, data):
	global score

	data = json.loads(data)
	#print(data)

	if "event" not in data:
		return

	event = data["event"]
	match event:
		case "new_wave":
			index = data["i"]
			spawns = data["spawns"]
			safe_pos = get_safe_pos(spawns)
			sio.emit("message", ("wave_completed", json.dumps({"playerY": safe_pos, "waveIndex": index})))

		case "score_up":
			score += 1
			print(f"Score: {score}/90")

		case "reward":
			print(f"Obtained flag: {data['flag']}")
			sio.disconnect()

		case "game_over":
			print("Solve failed")
			sio.disconnect()

@sio.event
def disconnect():
	print('disconnected from server')


sio.connect('https://URL/')
sio.wait()
```