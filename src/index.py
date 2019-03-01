from flask import Flask, render_template
import flask_socketio
from handler import Handler
import json
from const import *
app = Flask(__name__)
sio = flask_socketio.SocketIO(app)
handler = Handler(ggs)

@app.route('/')
def home():
    return render_template('index.html')

@sio.on('CLIENT_CONNECTION')
def handle_client_connection(data):
    print("New client connected")

@sio.on('message')
def handle_msg(data):

    global ggs

    action_gave = json.loads(data)

    if action_gave["action"] == "JOIN_GAME":
        resp = handler.take_action_join_game(action_gave)
        if len(ggs["players"]) < 6:
            flask_socketio.emit('message', resp, broadcast=True)
        else:
            flask_socketio.send(resp)

    elif action_gave["action"] == "RESET_GAME":
        resp = handler.take_action_reset_game(action_gave)
        flask_socketio.emit('message', resp, broadcast=True)

    elif action_gave["action"] == "START_GAME":
        handler.init_card_state(solution, guns, rooms, suspects)
        ggs = handler.init_move_state()

        resp = handler.take_action_reset_game()
        flask_socketio.emit('message', resp, broadcast=True)
        
    elif action_gave["action"] == "END_TURN":
        resp = handler.take_action_end_turn(action_gave)
        flask_socketio.emit('message', resp, broadcast=True)

    elif action_gave["action"] == "SUGGEST":
        resp = handler.take_action_suggest(action_gave)
        flask_socketio.emit('message', resp, broadcast=True)

    elif action_gave["action"] == "DISPROVE":
        resp = handler.take_action_disprove(action_gave)
        flask_socketio.emit('message', resp, broadcast=True)

    elif action_gave["action"] == "ACCUSE":
        resp = handler.take_action_accuse(action_gave, solution)
        if solution["weapon"] == action_gave["weapon"] and solution["suspect"] == action_gave["suspect"] and solution[
            "room"] == action_gave["room"]:
            flask_socketio.emit('message', resp, broadcast=True)
        else:
            flask_socketio.send(resp)
    else:
        resp = handler.take_action_undefined()
        flask_socketio.send(resp)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True, passthrough_errors=False)
