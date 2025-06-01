# Space Traveler
easy challenge made by **rootcan**

Description:

Votre meilleur ami a créé un jeu sur navigateur qu'il dit "impossible à finir". Prouvez-lui que le mauvais design n'est pas une bonne façon d'augmenter la difficulté de son jeu en obtenant un score de 90 !

> template.py
```python
# pip install "python-socketio[client]" requests websocket-client
import socketio

sio = socketio.Client()

@sio.event
def connect():
	pass


@sio.event
def message(msg_type, data):
	pass


@sio.event
def disconnect():
	pass

# to send a message:
# sio.emit("message", "game_start")

sio.connect('http://URL/')
sio.wait()

```

[Solve](SOLVE.md)