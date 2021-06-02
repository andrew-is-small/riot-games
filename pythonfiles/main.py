from typing import Dict, List, Tuple

import pandas as pd
import numpy as np
import requests
import json


# Custom Exceptions
class ResourceNotFoundException:
    pass

# TODO implement a player class that just holds all the JSONS and yeah.
# TODO cockulus class simply reads info from a players' jsons.

class CockulusClass:

    def __init__(self):
        # Configure the API Key
        config_file = 'res/config.json'
        with open(config_file, 'r') as file:
            config = json.load(file)
        self.api_key = config['api_key']

    # API GETTING METHODS
    def get_id_puuid(self, summoner_name: str) -> Tuple[str, str]:
        """Gets the puUID and ID of a person based on the summoner name.
        returns as a tuple(id, puuid)
        returns an empty string if nothing was found."""
        lonk = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners' \
               + '/by-name/' \
               + summoner_name + '?api_key=' + self.api_key
        puuid_to_ret = ''
        id_to_ret = ''
        sum_info = None
        try:
            sum_info = requests.get(lonk)
            if not sum_info.ok:
                raise ResourceNotFoundException
        except ResourceNotFoundException:
            print('Resource not found, code {code}'
                  .format(code=sum_info.status_code))
            return id_to_ret, puuid_to_ret
        if sum_info is not None:
            sum_info = sum_info.json()
            id_to_ret = sum_info['id']
            puuid_to_ret = sum_info['puuid']
        return id_to_ret, puuid_to_ret

    def get_last_games_metadata(self, n: int, puuid: str) -> List:
        """Gets last n games metadata.
        Formatted as a list of dictionaries(one dict for each game)"""
        # TODO implement this
        pass

    # TODO categorize json's that we collect with simple names

    # READING JSON METHODS
    def get_ranked_wr(self, jason: List) -> float:
        """Gets a summoner's ranked winrate from their json.
        Returns their ranked solo/duo winrate by default.
        If that is not found, returns their ranked flex winrate.
        If that is not found, returns -1

        json should be requested from
        https://na1.api.riotgames.com/lol/league/v4/entries/
        by-summoner/sumId?api_key=apiKey
        """
        sd_wins = jason[0]['wins']
        sd_losses = jason[0]['losses']
        flex_wins = jason[1]['wins']
        flex_losses = jason[1]['losses']
        if sd_wins + sd_losses > 0:
            return sd_wins / (sd_wins + sd_losses)
        elif flex_wins + flex_losses > 0:
            return flex_wins / (flex_wins + flex_losses)
        else:
            return -1


a = CockulusClass()
ide, puuide = a.get_id_puuid('PlatypusOfCanada')
print(ide, puuide)
