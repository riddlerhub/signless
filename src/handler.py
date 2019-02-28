import json,random,sys


class Handler:
    def __init__(self, global_game_state):
        self.ggs = global_game_state

    def take_action_join_game(self, action_gave):
        player_name = action_gave["payload"]["playerName"]
        if not player_name in self.ggs["players"]:

            if len(self.ggs["players"]) < 6:
                self.ggs["players"].append(player_name)
                response_dict = {
                    "responseToken": "PLAYER_JOINED_GAME",
                    "payload": player_name,
                    "gameState": self.ggs
                }
                resp = json.dumps(response_dict)
            else:
                response_dict = {
                    "responseToken": "MAXIMUM_PLAYER_REACHED",
                    "payload": player_name,
                    "gameState": self.ggs
                }
                resp = json.dumps(response_dict)
        else:
            response_dict = {
                "responseToken": "PLAYER_ALREADY_JOINED",
                "payload": player_name,
                "gameState": self.ggs
            }
            resp = json.dumps(response_dict)
        return resp

    def take_action_reset_game(self, action_gave):
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
        return resp

    def take_action_reset_game(self):

        for player in self.ggs["players"]:
            self.ggs["can_accuse"][player] = True;

        print(self.ggs)

        self.ggs["current_player"] = self.ggs["players"][0]
        response_dict = {
            "responseToken": "GAME_STARTED_STATE",
            "payload": "Game Started",
            "gameState": self.ggs
        }
        resp = json.dumps(response_dict)
        return resp

    def take_action_end_turn(self, action_gave):
        self.ggs["movement_info"]["current_locations"] = action_gave["payload"]["current_locations"]
        self.ggs["solution"] = dict()
        self.ggs["turn"] += 1
        self.ggs["current_player"] = self.ggs["players"][
            self.ggs["turn"] % len(self.ggs["players"])]
        response_dict = {
            "responseToken": "SUGGEST_STATE",
            "payload": "Turn Ended",
            "gameState": self.ggs
        }
        resp = json.dumps(response_dict)
        return resp

    def take_action_suggest(self, action_gave):
        print("Player {} suggested the murder took place in {}, with {} using {}".format(
            self.ggs["current_player"], "CURRENT ROOM", action_gave["suspect"], action_gave["weapon"]))
        self.ggs["current_suggestion"]["suspect"] = action_gave["suspect"]
        self.ggs["current_suggestion"]["weapon"] = action_gave["weapon"]
        self.ggs["current_suggestion"]["room"] = action_gave["room"]
        locations = action_gave["locations"]
        suspect = action_gave["suspect"]
        current_player = self.ggs["current_player"]
        current_player_character = self.ggs["movement_info"]["associations"][current_player]
        locations[suspect] = locations[current_player_character]
        self.ggs["movement_info"]["current_locations"] = locations

        # Set the suspect's location to the
        for player in self.ggs["players"]:
            if not (player == self.ggs["current_player"]):
                if action_gave["weapon"] in self.ggs["player_cards"][player]:
                    print("{} can disprove using {}".format(player, action_gave["weapon"]))
                    if player not in self.ggs["can_disprove"]:
                        self.ggs["can_disprove"][player] = [action_gave["weapon"]]
                    else:
                        self.ggs["can_disprove"][player].append(action_gave["weapon"])
                if action_gave["suspect"] in self.ggs["player_cards"][player]:
                    print("{} can disprove using {}".format(player, action_gave["suspect"]))
                    if player not in self.ggs["can_disprove"]:
                        self.ggs["can_disprove"][player] = [action_gave["suspect"]]
                    else:
                        self.ggs["can_disprove"][player].append(action_gave["suspect"])
                # Location
                if action_gave["room"] in self.ggs["player_cards"][player]:
                    print("{} can disprove using {}".format(player, action_gave["room"]))
                    if player not in self.ggs["can_disprove"]:
                        self.ggs["can_disprove"][player] = [action_gave["room"]]
                    else:
                        self.ggs["can_disprove"][player].append(action_gave["room"])

        next_player_index = (self.ggs["players"].index(self.ggs["current_player"]) + 1) % len(
            self.ggs["players"])
        self.ggs["disproving_player"] = self.ggs["players"][next_player_index]

        response_dict = {
            "responseToken": "PRE_DISPROVE",
            "payload": "Pre Disprove State",
            "gameState": self.ggs
        }
        resp = json.dumps(response_dict)
        return resp

    def take_action_disprove(self, action_gave):
        disprove_value = action_gave["disproveValue"]
        if disprove_value == "novalue":
            next_player_index = (self.ggs["players"].index(self.ggs["disproving_player"]) + 1) % len(
                self.ggs["players"])
            self.ggs["disproving_player"] = self.ggs["players"][next_player_index]
            if not self.ggs["disproving_player"] == self.ggs["current_player"]:
                response_dict = {
                    "responseToken": "DISPROVE_STATE",
                    "payload": "Disprove State",
                    "gameState": self.ggs
                }
                resp = json.dumps(response_dict)
            else:
                print("No player can disprove {}".format(self.ggs["current_player"]))
                self.ggs["can_disprove"] = dict()
                response_dict = {
                    "responseToken": "ACCUSE_STATE",
                    "payload": "disproveFailed",
                    "gameState": self.ggs
                }
                resp = json.dumps(response_dict)

        else:
            print("{} can disprove using {}".format(self.ggs["disproving_player"], disprove_value))
            self.ggs["can_disprove"] = dict()
            response_dict = {
                "responseToken": "ACCUSE_STATE",
                "payload": "{} disproved you using {}".format(self.ggs["disproving_player"], disprove_value),
                "gameState": self.ggs
            }
            resp = json.dumps(response_dict)
        return resp

    def take_action_accuse(self,action_gave,solution):
        print('{} accused {} of the murder using {} in {}.'.format(self.ggs["current_player"],
                                                                   action_gave["suspect"],
                                                                   action_gave["weapon"],
                                                                   action_gave["room"]))
        self.ggs["accusation"]["weapon"] = action_gave["weapon"]
        self.ggs["accusation"]["suspect"] = action_gave["suspect"]
        self.ggs["accusation"]["room"] = action_gave["room"]

        if solution["weapon"] == action_gave["weapon"] and solution["suspect"] == action_gave["suspect"] and solution[
            "room"] == action_gave["room"]:
            self.ggs["game_ended"] = True
            response_dict = {
                "responseToken": "ACCUSE_SUCCESS",
                "payload": "Accuse Success",
                "gameState": self.ggs
            }
            resp = json.dumps(response_dict)

        else:
            self.ggs["can_accuse"][self.ggs["current_player"]] = False
            print(self.ggs["can_accuse"])
            self.ggs["game_ended"] = not any(self.ggs["can_accuse"].values())

            print(self.ggs["game_ended"])
            self.ggs["solution"] = solution
            response_dict = {
                "responseToken": "ACCUSE_FAILURE",
                "payload": "Accuse Failure",
                "gameState": self.ggs
            }
            resp = json.dumps(response_dict)
        return resp

    def take_action_undefined(self):
        response_dict = {
            "responseToken": "UNIDENTIFIED_ACTION",
            "payload": "Unidentified action",
            "gameState": self.ggs
        }
        resp = json.dumps(response_dict)
        return resp

    def init_card_state(self, solution, guns, rooms, suspects):
        self.ggs["player_cards"] = dict()

        random.shuffle(guns)
        random.shuffle(rooms)
        random.shuffle(suspects)

        solution["weapon"] = guns[0]
        solution["room"] = rooms[0]
        solution["suspect"] = suspects[0]

        combined_cards = guns[1:len(guns)] + rooms[1:len(rooms)] + suspects[1:len(suspects)]
        print(solution)

        random.shuffle(combined_cards)

        r = len(combined_cards) % len(self.ggs["players"])
        q = len(combined_cards) / len(self.ggs["players"])
        start = 0
        stop = q
        for player in self.ggs["players"]:
            if r > 0:
                stop += 1
                r -= 1
            self.ggs["player_cards"][player] = combined_cards[start:stop]
            start = stop
            stop += q

    def init_move_state(self):
        initial_state = self.ggs
        assocs = {}
        assoc_chars = []
        unassigned = []
        try:
            starting_locations = {
                "plum": {"x": 112, "y": 158},
                "white": {"x": 360, "y": 384},
                "peacock": {"x": 114, "y": 356},
                "green": {"x": 167, "y": 384},
                "scarlet": {"x": 351, "y": 107},
                "mustard": {"x": 411, "y": 168}
            }

            index = 0
            characters = starting_locations.keys()

            for player in self.ggs["players"]:
                assocs[player] = characters[index]
                assoc_chars.append(characters[index])
                index += 1

            if not len(assocs) == len(characters):
                for index in range(len(characters)):
                    if not characters[index] in assoc_chars:
                        unassigned.append(characters[index])
            self.ggs["movement_info"] = {
                "associations": assocs,
                "current_locations": starting_locations,
                "unassigned_characters": unassigned
            }
            return self.ggs
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return initial_state