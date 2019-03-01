class Setter:
    def __init__(self):
        pass

    def set_begining_locations(self):
        bl = {
            "plum": {"x": 112, "y": 158},
            "white": {"x": 360, "y": 384},
            "peacock": {"x": 114, "y": 356},
            "green": {"x": 167, "y": 384},
            "scarlet": {"x": 351, "y": 107},
            "mustard": {"x": 411, "y": 168}
        }
        return bl

    def set_combined_cards(self, guns, rooms, suspects):
        res = guns[1:len(guns)] + rooms[1:len(rooms)] + suspects[1:len(suspects)]
        return res

    def set_player_name(self, action_gave):
        res = action_gave["payload"]["playerName"]
        return res

    def set_current_location(self, action_gave):
        res = action_gave["payload"]["current_locations"]
        return res