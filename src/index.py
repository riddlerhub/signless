from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
import json
import random
import sys
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Wrap the flask socket io middleware
socketio = SocketIO(app)

global_game_state = {
    "players": [],
    "turn": 0,
    "current_player": "",
    "player_cards": dict(),
    "current_suggestion": dict(),
    "can_disprove": dict(),
    "disproving_player": "",
    "can_accuse": dict(),
    "accusation": dict(),
    "solution": dict(),
    "game_ended": False
}

guns = ["candlestick", "revolver",
           "rope", "wrench",
           "lead_pipe", "knife"]

rooms = ["study", "library", "conservatory",
         "hall", "kitchen", "ballroom",
         "dining_room", "lounge", "billiard_room"]

suspects = ["white", "peacock",
            "scarlet", "mustard",
            "green", "plum"]

solution = {
    "weapon": "",
    "room": "",
    "suspect": ""
}


@app.route('/')
def game_view():
    return render_template('index.html', title="Home")

@socketio.on('CLIENT_CONNECTION')
def handle_client_connection(data):
    print("New client connected")

@socketio.on('message')
def handle_msg(data):

    global global_game_state

    action_gave = json.loads(data)

    if action_gave["action"] == "JOIN_GAME":
        player_name = action_gave["payload"]["playerName"]
        if not player_name in global_game_state["players"]:

            if len(global_game_state["players"]) < 6:
                global_game_state["players"].append(player_name)
                response_dict = {
                    "responseToken": "PLAYER_JOINED_GAME",
                    "payload": player_name,
                    "gameState": global_game_state
                }
                resp = json.dumps(response_dict)
                emit('message', resp, broadcast=True)
            else:
                response_dict = {
                    "responseToken": "MAXIMUM_PLAYER_REACHED",
                    "payload": player_name,
                    "gameState": global_game_state
                }
                resp = json.dumps(response_dict)
                send(resp)
        else:
            response_dict = {
                "responseToken": "PLAYER_ALREADY_JOINED",
                "payload": player_name,
                "gameState": global_game_state
            }
            resp = json.dumps(response_dict)
            send(resp)
    elif action_gave["action"] == "RESET_GAME":
        global_game_state = {
            "players": [],
            "turn": 0,
            "current_player": "",
            "player_cards": dict(),
            "current_suggestion": dict(),
            "can_disprove": dict(),
            "disproving_player": "",
            "can_accuse": dict(),
            "accusation": dict(),
            "solution": dict(),
            "game_ended": False
        }
        response_dict = {
                "responseToken": "CLEARED_GAME_STATE",
                "payload": "Cleared game state",
                "gameState": global_game_state
        }
        resp = json.dumps(response_dict)
        emit('message', resp, broadcast=True)

    elif action_gave["action"] == "START_GAME":
        # createSolution()
        # print(solution)
        # assignCards()
        initialize_card_state()
        global_game_state = initialize_movement_state(global_game_state)

        for player in global_game_state["players"]:
            global_game_state["can_accuse"][player] = True;

        print(global_game_state)

        global_game_state["current_player"] = global_game_state["players"][0]
        response_dict = {
            "responseToken": "GAME_STARTED_STATE",
            "payload": "Game Started",
            "gameState": global_game_state
        }
        resp = json.dumps(response_dict)
        emit('message', resp, broadcast=True)
        
    elif action_gave["action"] == "END_TURN":
        global_game_state["movement_info"]["current_locations"] = action_gave["payload"]["current_locations"]
        global_game_state["solution"] = dict()
        global_game_state["turn"] += 1
        global_game_state["current_player"] = global_game_state["players"][global_game_state["turn"] % len(global_game_state["players"])]
        response_dict = {
            "responseToken": "SUGGEST_STATE",
            "payload": "Turn Ended",
            "gameState": global_game_state
        }
        resp = json.dumps(response_dict)
        emit('message', resp, broadcast=True)
    elif action_gave["action"] == "SUGGEST":
        print("Player {} suggested the murder took place in {}, with {} using {}".format(global_game_state["current_player"], "CURRENT ROOM", action_gave["suspect"], action_gave["weapon"]))
        global_game_state["current_suggestion"]["suspect"] = action_gave["suspect"]
        global_game_state["current_suggestion"]["weapon"] = action_gave["weapon"]
        global_game_state["current_suggestion"]["room"] = action_gave["room"]
        locations = action_gave["locations"]
        suspect = action_gave["suspect"]
        current_player = global_game_state["current_player"]
        current_player_character = global_game_state["movement_info"]["associations"][current_player]
        locations[suspect] = locations[current_player_character]
        global_game_state["movement_info"]["current_locations"] = locations

        # Set the suspect's location to the 
        for player in global_game_state["players"]:
            if not (player == global_game_state["current_player"]):
                if action_gave["weapon"] in global_game_state["player_cards"][player]:
                    print("{} can disprove using {}".format(player, action_gave["weapon"]))
                    if player not in global_game_state["can_disprove"]:
                        global_game_state["can_disprove"][player] = [action_gave["weapon"]]
                    else:
                        global_game_state["can_disprove"][player].append(action_gave["weapon"])
                if action_gave["suspect"] in global_game_state["player_cards"][player]:
                    print("{} can disprove using {}".format(player, action_gave["suspect"]))
                    if player not in global_game_state["can_disprove"]:
                        global_game_state["can_disprove"][player] = [action_gave["suspect"]]
                    else:
                        global_game_state["can_disprove"][player].append(action_gave["suspect"])
                # Location
                if action_gave["room"] in global_game_state["player_cards"][player]:
                    print("{} can disprove using {}".format(player, action_gave["room"]))
                    if player not in global_game_state["can_disprove"]:
                        global_game_state["can_disprove"][player] = [action_gave["room"]]
                    else:
                        global_game_state["can_disprove"][player].append(action_gave["room"])

        next_player_index = (global_game_state["players"].index(global_game_state["current_player"]) + 1) % len(global_game_state["players"])
        global_game_state["disproving_player"] = global_game_state["players"][next_player_index]

        response_dict = {
            "responseToken": "PRE_DISPROVE",
            "payload": "Pre Disprove State",
            "gameState": global_game_state
        }
        resp = json.dumps(response_dict)
        emit('message', resp, broadcast=True)
    elif action_gave["action"] == "DISPROVE":
        disprove_value = action_gave["disproveValue"]
        if disprove_value == "novalue":
            next_player_index = (global_game_state["players"].index(global_game_state["disproving_player"]) + 1) % len(global_game_state["players"])
            global_game_state["disproving_player"] = global_game_state["players"][next_player_index]
            if not global_game_state["disproving_player"] == global_game_state["current_player"]:
                response_dict = {
                    "responseToken": "DISPROVE_STATE",
                    "payload": "Disprove State",
                    "gameState": global_game_state
                }
                resp = json.dumps(response_dict)
                emit('message', resp, broadcast=True)
            else:
                print("No player can disprove {}".format(global_game_state["current_player"]))
                global_game_state["can_disprove"] = dict()
                response_dict = {
                    "responseToken": "ACCUSE_STATE",
                    "payload": "disproveFailed",
                    "gameState": global_game_state
                }
                resp = json.dumps(response_dict)
                emit('message', resp, broadcast=True)
        else:
            print("{} can disprove using {}".format(global_game_state["disproving_player"], disprove_value))
            global_game_state["can_disprove"] = dict()
            response_dict = {
                "responseToken": "ACCUSE_STATE",
                "payload": "{} disproved you using {}".format(global_game_state["disproving_player"], disprove_value),
                "gameState": global_game_state
            }
            resp = json.dumps(response_dict)
            emit('message', resp, broadcast=True)
    elif action_gave["action"] == "ACCUSE":
        print('{} accused {} of the murder using {} in {}.'.format(global_game_state["current_player"],
                                                                   action_gave["suspect"],
                                                                   action_gave["weapon"],
                                                                   action_gave["room"]))
        global_game_state["accusation"]["weapon"] = action_gave["weapon"]
        global_game_state["accusation"]["suspect"] = action_gave["suspect"]
        global_game_state["accusation"]["room"] = action_gave["room"]

        if (solution["weapon"] == action_gave["weapon"] and solution["suspect"] == action_gave["suspect"] and solution["room"] == action_gave["room"]):
            # accuse correct, congrats
                global_game_state["game_ended"] = True
                response_dict = {
                    "responseToken": "ACCUSE_SUCCESS",
                    "payload": "Accuse Success",
                    "gameState": global_game_state
                }
                resp = json.dumps(response_dict)
                emit('message', resp, broadcast=True)
        else:
            global_game_state["can_accuse"][global_game_state["current_player"]] = False
            print(global_game_state["can_accuse"])
            global_game_state["game_ended"] = not any(global_game_state["can_accuse"].values())

            print(global_game_state["game_ended"])
            global_game_state["solution"] = solution
            response_dict = {
                "responseToken": "ACCUSE_FAILURE",
                "payload": "Accuse Failure",
                "gameState": global_game_state
            }
            resp = json.dumps(response_dict)
            send(resp)
    else:
        response_dict = {
            "responseToken": "UNIDENTIFIED_ACTION",
            "payload": "Unidentified action",
            "gameState": global_game_state
        }
        resp = json.dumps(response_dict)
        send(resp)

def initialize_card_state():
    global solution
    global guns
    global rooms
    global suspects
    global global_game_state

    global_game_state["player_cards"] = dict()

    random.shuffle(guns)
    random.shuffle(rooms)
    random.shuffle(suspects)

    solution["weapon"] = guns[0]
    solution["room"] = rooms[0]
    solution["suspect"] = suspects[0]

    combined_cards = guns[1:len(guns)] + rooms[1:len(rooms)] + suspects[1:len(suspects)]
    print(solution)

    random.shuffle(combined_cards)

    r = len(combined_cards) % len(global_game_state["players"])
    q = len(combined_cards) / len(global_game_state["players"])
    start = 0
    stop = q
    for player in global_game_state["players"]:
        if r > 0:
            stop += 1
            r -= 1
        global_game_state["player_cards"][player] = combined_cards[start:stop]
        start = stop
        stop += q

def initialize_movement_state(global_game_state):
    initialState = global_game_state
    try:
        starting_locations = {
            "plum": {"x": 112, "y": 158},
            "white": {"x": 360, "y": 384},
            "peacock": {"x": 114, "y": 356},
            "green": {"x": 167, "y": 384},
            "scarlet": {"x": 351, "y": 107},
            "mustard": {"x": 411, "y": 168}
        }
        associations = dict()
        associated_characters = list()
        index = 0
        characters = starting_locations.keys()
        # Make the player association with the piece
        for player in global_game_state["players"]:
            associations[player] = characters[index]
            associated_characters.append(characters[index])
            index += 1
        unassigned = list()
        if not len(associations) == len(characters):
            for ii in range(len(characters)):
                if not characters[ii] in associated_characters:
                    unassigned.append(characters[ii])
        global_game_state["movement_info"] = {
            "associations": associations,
            "current_locations": starting_locations,
            "unassigned_characters": unassigned
        }
        return global_game_state
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return initialState

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True, passthrough_errors=False)
