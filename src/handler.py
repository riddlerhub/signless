import random,sys
from core import generate
from core import setter
generate = generate.generate()
setter = setter.Setter()


class Handler:
    def __init__(self, global_game_state):
        self.ggs = global_game_state
        self.assocs = {}
        self.assoc_chars = []
        self.unassigned = []

    def take_action_join_game(self, action_gave):
        player_name = setter.set_player_name(action_gave)
        if not player_name in self.ggs["players"]:

            if len(self.ggs["players"]) < 6:
                self.ggs["players"].append(player_name)
                resp = generate.generate_player_joined_game_resp(player_name, self.ggs)
            else:
                resp = generate.generate_maximum_player_reached_resp(player_name, self.ggs)
        else:
            resp = generate.generate_player_already_joined(player_name, self.ggs)
        return resp

    def take_action_reset_game(self, action_gave):
        resp = generate.generate_cleared_game_state_resp()
        return resp

    def take_action_reset_game(self):
        for player in self.ggs["players"]:
            self.ggs["can_accuse"][player] = True;

        self.ggs["current_player"] = self.ggs["players"][0]
        resp = generate.generate_game_started_state_resp(self.ggs)
        return resp

    def take_action_end_turn(self, action_gave):
        self.ggs["movement_info"]["current_locations"] = setter.set_current_location(action_gave)
        self.ggs["solution"] = {}
        self.ggs["turn"] += 1
        self.ggs["current_player"] = self.ggs["players"][
            self.ggs["turn"] % len(self.ggs["players"])]

        resp = generate.generate_suggest_state_resp(self.ggs)
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

        resp = generate.generate_pre_disprove_resp(self.ggs)
        return resp

    def take_action_disprove(self, action_gave):
        disprove_value = action_gave["disproveValue"]
        if disprove_value == "novalue":
            next_player_index = (self.ggs["players"].index(self.ggs["disproving_player"]) + 1) % len(
                self.ggs["players"])
            self.ggs["disproving_player"] = self.ggs["players"][next_player_index]
            if not self.ggs["disproving_player"] == self.ggs["current_player"]:
                resp = generate.generate_disprove_state_resp(self.ggs)
            else:
                print("No player can disprove {}".format(self.ggs["current_player"]))
                self.ggs["can_disprove"] = {}
                resp = generate.generate_accuse_state_resp(self.ggs)

        else:
            print("{} can disprove using {}".format(self.ggs["disproving_player"], disprove_value))
            self.ggs["can_disprove"] = {}
            resp = generate.generate_accuse_state_resp(self.ggs)
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
            resp = generate.generate_accuse_success_resp(self.ggs)

        else:
            self.ggs["can_accuse"][self.ggs["current_player"]] = False
            print(self.ggs["can_accuse"])
            self.ggs["game_ended"] = not any(self.ggs["can_accuse"].values())

            print(self.ggs["game_ended"])
            self.ggs["solution"] = solution

            resp = generate.generate_accuse_failure_resp(self.ggs)
        return resp

    def take_action_undefined(self):
        resp = generate.generate_unidentified_action(self.ggs)
        return resp

    def init_card_state(self, solution, guns, rooms, suspects):
        self.ggs["player_cards"] = {}

        self.random_shuffle_guns_suspects_rooms(guns, suspects,rooms)

        solution["weapon"] = guns[0]
        solution["room"] = rooms[0]
        solution["suspect"] = suspects[0]

        combined_cards = setter.set_combined_cards(guns, rooms, suspects)
        self.random_shuffle_cards(combined_cards)

        r = generate.generate_r(self.ggs,combined_cards)
        q = generate.generate_q(self.ggs,combined_cards)
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
        try:
            bl = setter.set_begining_locations()
            index = 0
            characters = bl.keys()

            for player in self.ggs["players"]:
                self.assocs[player] = characters[index]
                self.assoc_chars.append(characters[index])
                index += 1

            if not len(self.assocs) == len(characters):
                for index in range(len(characters)):
                    if not characters[index] in self.assoc_chars:
                        self.unassigned.append(characters[index])
            self.ggs["movement_info"] = {
                "associations": self.assocs,
                "current_locations": bl,
                "unassigned_characters": self.unassigned
            }
            return self.ggs
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return initial_state

    def random_shuffle_guns_suspects_rooms(self,guns,suspects,rooms):
        random.shuffle(guns)
        random.shuffle(rooms)
        random.shuffle(suspects)

    def random_shuffle_cards(self, combined_cards):
        random.shuffle(combined_cards)