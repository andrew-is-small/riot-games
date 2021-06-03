from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
import numpy as np
import requests
import json


class YouAreDumbOrSomethingError(Exception):
    pass


class Player:
    """A League player and his JSONs.

    ===== Public Attributes =====
    api_key: your api key. Give it to me.
    name: the summoner name
    n: number of games you want data for
    sum_info: basic summoner info
    ranked_info: ranked information such as winrate, games played
    match_info: jsons for the past n matches.
    """

    def __init__(self, api_key, name, n):
        """Creates a new player and gets all the JSONs set up.
        name is the summoner name of the player
        n is the number of games you want to look back at."""
        self.api_key = api_key
        self.name = name
        self.n = n

        self.sum_info = self.get_sum_info(self.name)
        if self.sum_info is None:
            raise YouAreDumbOrSomethingError(f'Summoner info not found for '
                                             f'{self.name}')
        self.ranked_info = self.get_ranked_info(self.sum_info['id'])
        self.match_info = self.get_match_infos(self.sum_info['puuid'])
        if self.match_info is None or self.ranked_info is None:
            print("Warning, match info OR ranked info was not found.")

    # basic summoner info
    def get_sum_info(self, summoner_name: str) -> Optional[Dict]:
        """Gets basic summoner info, such as id, account id, puuid
        For a summoner name.
        Returns None if it got an error code."""

        lonk = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners' \
               + '/by-name/' \
               + summoner_name + '?api_key=' + self.api_key
        sum_info = requests.get(lonk)
        return error_or_json(sum_info)

    def get_ranked_info(self, sum_id: str) -> Optional[Dict]:
        """Gets ranked info, such as queue type, wins/losses
        using the 'id' from get_sum_info output.
        Returns None if not code 200."""
        rank_info = requests. \
            get('https://na1.api.riotgames.com/'
                'lol/league/v4/entries/by-summoner/' + sum_id + '?api_key=' +
                self.api_key)
        return error_or_json(rank_info)

    # TODO you potentially have to find the last n summoners rift matches.
    # TODO ensure you either have n matches in the list, or 0
    def get_match_infos(self, puuid: str) -> Optional[List]:
        """Gets match information for the past n matches.
        Formatted as a list of dictionaries(I think)
        Precondition: n > 0
        note that uh...
        matchdata['metadata']['participants'].index(puuId) then
        matchdata['metadata']['participants][index] is the player's stats.
        """
        n = self.n
        hmga = '0'
        # useless variable, may change later but yeah
        # List of game ids to look at
        game_ids = requests.get('https://americas.api.riotgames.com/lol/match'
                                '/v5/matches/by-puuid/' + puuid + '/ids' +
                                '?api_key=' + self.api_key + '&start=' +
                                hmga + '&count=' + str(n))
        # So it starts at hmga ago and goes back n games.

        game_ids = error_or_json(game_ids)
        # this is some dumb shit
        match_data = []
        if game_ids is None:
            return None
        for gameid in game_ids:
            dada = requests.get('https://americas.api.riotgames.com/lol/'
                                'match/v5/matches/' +
                                gameid + '?api_key=' + self.api_key)
            a = error_or_json(dada)
            if a is not None:
                match_data.append(a)
        return None if len(match_data) == 0 else match_data


class Game:
    """A League game with 2 teams of 5 players.
    This class will literally just hold two lists with 5 player objects
    in each list.

    ===== Public Attributes =====
    ally: A list comprising of allied players
    enemy: A list comprising of enemy players
    """
    pass


class GameAnalysis:
    """An Analysis guy for a game of League of Legends.
    This class has tools for unpacking previous JSONs to get
    important metrics for a specific game."""

    def __init__(self, api_key):
        # Configure the API Key
        self.api_key = api_key
        config_file = 'res/config.json'

    # API GETTING METHODS

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


def error_or_json(thing: requests.Response) -> Optional[Union[Dict, List]]:
    if not thing.ok:
        print('Resource not found, code {code}'
              .format(code=thing.status_code))
        return None
    return thing.json()


def load_config(config_file) -> Dict:
    """Right now, it just returns the API key. Idk what else to do with it"""
    with open(config_file, 'r') as file:
        config = json.load(file)
        return config
