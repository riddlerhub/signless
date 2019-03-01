import json
from const import *


class generate:
    def __init__(self):
        self.resTokens = resTokens
        self.payloadStrs = payloadStrs
        self.resp = {}

    def generate_player_joined_game_resp(self, player_name, ggs):
        self.resp = {
            "responseToken": self.resTokens['pjg'],
            "payload": player_name,
            "gameState": ggs
        }
        return json.dumps(self.resp)

    def generate_maximum_player_reached_resp(self, player_name, ggs):
        resp = {
            "responseToken": self.resTokens['mpr'],
            "payload": player_name,
            "gameState": ggs
        }
        return json.dumps(resp)

    def generate_player_already_joined(self, player_name, ggs):
        resp = {
            "responseToken": self.resTokens['paj'],
            "payload": player_name,
            "gameState": ggs
        }
        return json.dumps(resp)

    def generate_cleared_game_state_resp(self):
        ggs = self.reset_ggs_payload()
        resp = {
            "responseToken": self.resTokens['cgs'],
            "payload": self.payloadStrs ,
            "gameState": ggs
        }
        return json.dumps(resp)

    def generate_game_started_state_resp(self,ggs):
        resp = {
            "responseToken": self.resTokens['gss'],
            "payload": self.payloadStrs['gs'],
            "gameState": ggs
        }
        return json.dumps(resp)

    def generate_suggest_state_resp(self, ggs):
        resp = {
            "responseToken": self.resTokens['ss'],
            "payload": self.payloadStrs['te'],
            "gameState": ggs
        }
        return json.dumps(resp)

    def generate_pre_disprove_resp(self, ggs):
        resp = {
            "responseToken": self.resTokens['pd'],
            "payload": self.payloadStrs['pds'],
            "gameState": ggs
        }
        resp = json.dumps(resp)
        return resp

    def generate_accuse_state_resp(self, ggs):
        resp = {
            "responseToken": self.resTokens['as'],
            "payload": "{} disproved you using {}".format(self.ggs["disproving_player"]),
            "gameState": ggs
        }
        return json.dumps(resp)

    def generate_accuse_success_resp(self, ggs):
        resp = {
            "responseToken": self.resTokens['ass'],
            "payload": self.payloadStrs['as'] ,
            "gameState": ggs
        }
        return json.dumps(resp)

    def generate_accuse_failure_resp(self, ggs):
        resp = {
            "responseToken": self.resTokens['af'],
            "payload": self.payloadStrs['af'],
            "gameState": ggs
        }
        return json.dumps(resp)

    def generate_unidentified_action(self, ggs):
        resp = {
            "responseToken": self.resTokens['ua'],
            "payload": self.payloadStrs['ua'],
            "gameState": ggs
        }
        return json.dumps(resp)

    def generate_disprove_state_resp(self, ggs):
        resp = {
            "responseToken": self.resTokens['ds'],
            "payload": self.payloadStrs['ds'],
            "gameState": self.ggs
        }
        return json.dumps(resp)

    def geneerate_accuse_state_resp(self, ggs):
        resp = {
            "responseToken": self.resTokens['as'],
            "payload": self.payloadStrs['df'],
            "gameState": self.ggs
        }
        return json.dump(resp)

    def reset_ggs_payload(self):
        ggs = {
            "players": [],
            "turn": 0,
            "current_player": "",
            "player_cards": {},
            "current_suggestion": {},
            "can_disprove": {},
            "disproving_player": "",
            "can_accuse": {},
            "accusation": {},
            "solution": {},
            "game_ended": False
        }
        return ggs

    def generate_r(self, combined_cards):
        return len(combined_cards) % len(self.ggs["players"])

    def generate_q(self, combined_cards):
        return len(combined_cards) / len(self.ggs["players"])