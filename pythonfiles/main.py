import statistics
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import time
import requests
import json


class YouAreDumbOrSomethingError(Exception):
    pass


# name: Player.
player_objects = {}


class Player:
    """A League player and his JSONs.

    ===== Public Attributes =====
    api_key: your api key. Give it to me.
    name: the summoner name(string)
    n: number of games you want data for
    sum_info: basic summoner info(json)
    ranked_info: ranked information such as winrate, games played(json)
    match_info: list of game jsons for the past n matches.

    === Useful Methods ===
    get_ranked_wr: float
    is_veteran: boolean
    is_hotstreak: boolean

    === Helper Methods ===
    kda: finds player's kda in a game from the json
    win: finds if a player won a game from the json
    """

    def __init__(self, api_key, name, n):
        """Creates a new player and gets all the JSONs set up.
        name is the summoner name of the player
        n is the number of games you want to look back at."""
        self.api_key = api_key

        # Andrew says if there's a space in the name we just delete it
        self.name = name.replace(' ', '')
        self.n = n

        self.sum_info = self.get_sum_info(self.name)
        if self.sum_info is None:
            raise YouAreDumbOrSomethingError(f'Summoner info not found for '
                                             f'{self.name}')
        self.ranked_info = self.get_ranked_info(self.sum_info['id'])
        self.match_info = self.get_match_infos(self.sum_info['puuid'])
        if self.match_info is None or self.ranked_info is None:
            print("Warning, match info OR ranked info was not found.")

    # DEFINITELY USEFUL METHODS
    def get_ranked_wr(self) -> Optional[float]:
        """Gets a summoner's ranked winrate from their json.
        Returns their ranked solo/duo winrate by default.
        If that is not found, returns their ranked flex winrate.
        If that is not found, returns None
        """
        jason = self.ranked_info
        sd_wins = jason[0]['wins']
        sd_losses = jason[0]['losses']
        if len(jason) > 1:
            flex_wins = jason[1]['wins']
            flex_losses = jason[1]['losses']
        if sd_wins + sd_losses > 0:
            return sd_wins / (sd_wins + sd_losses)
        elif len(jason) > 1 and flex_wins + flex_losses > 0:
            return flex_wins / (flex_wins + flex_losses)
        else:
            return None

    def is_veteran(self):
        """Returns whether or not this player is a 'veteran'
        (aka hardstuck basically)"""
        for i in range(0, len(self.ranked_info)):
            if self.ranked_info[i]['veteran']:
                return True
        return False

    def is_hotstreak(self):
        """Returns whether or not the player is hotstreaking(3+ game winstreak)
        """
        for i in range(0, len(self.ranked_info)):
            if self.ranked_info[i]['hotStreak']:
                return True
        return False

    # POTENTIALLY USEFUL METHODS
    def kda(self, game: Dict) -> Tuple[int, int, int]:
        """Get's the KDA of the player, based on their puuid, for one game.
        The game should be from self.match_infos.
        """
        puuid = self.sum_info['puuid']
        for i in range(0, len(game['metadata']['participants'])):
            if game['metadata']['participants'][i] == puuid:
                c = i
        b = game['info']['participants'][c]
        k = b['kills']
        d = b['deaths']
        a = b['assists']
        return k, d, a

    def win(self, game: Dict) -> bool:
        """Returns true or false based on whether or not the player
        won a game. Games should be from self.match_info"""
        puuid = self.sum_info['puuid']
        for i in range(0, len(game['metadata']['participants'])):
            if game['metadata']['participants'][i] == puuid:
                c = i
        b = game['info']['participants'][c]
        w = b['win']
        return w

    # LOADING JSON METHODS
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

    def get_match_infos(self, puuid: str) -> Optional[List]:
        """Gets match information for the past n matches.
        Searches the last 'few' games for summoners rift matches.
        Formatted as a list of dictionaries(I think)
        Precondition: 0 < n < 20
        note that uh...
        matchdata['metadata']['participants'].index(puuId) then
        matchdata['metadata']['participants][index] is the player's stats.
        """
        # how far back should we check??
        how_far = '30'
        # hmga is 1 for now to avoid issues with getting data from the
        # current game that a player is in. We just won't deal with that ever.
        hmga = '1'

        # List of game ids to look at
        game_ids = requests.get('https://americas.api.riotgames.com/lol/match'
                                '/v5/matches/by-puuid/' + puuid + '/ids' +
                                '?api_key=' + self.api_key + '&start=' +
                                hmga + '&count=' + how_far)
        # So it starts at hmga ago and goes back n games.

        game_ids = error_or_json(game_ids)
        counterc = 0
        # this is some dumb shit
        match_data = []
        if game_ids is None:
            return None
        for gameid in game_ids:
            time.sleep(1)
            dada = requests.get('https://americas.api.riotgames.com/lol/'
                                'match/v5/matches/' +
                                gameid + '?api_key=' + self.api_key)
            a = error_or_json(dada)
            if a is not None and a['info']['gameMode'] == 'CLASSIC':
                match_data.append(a)
                counterc += 1
                print(f'[{self.name}]Found {counterc} games total: '
                      f'({a["info"]["gameMode"]})')
            else:
                print(f'[{self.name}]{gameid} was not a summoners rift game,'
                      f'({a["info"]["gameMode"]})')
            if counterc == self.n:
                break
        if counterc < self.n:
            print(f'[Player]Warning: {self.n} games requested, only found '
                  f'{counterc} games for {self.name}')
        return None if len(match_data) == 0 else match_data

    # NOT IN USE METHODS
    def get_match_binfos(self, puuid: str) -> Optional[List]:

        n = self.n

        a = 0
        b = 0
        match_data = []
        lg = requests.get('https://americas.api.riotgames.com/lol/match'
                          '/v5/matches/by-puuid/' + puuid + '/ids' +
                          '?api_key=' + self.api_key + '&start=' +
                          str(b) + '&count=50')

        while a < n and b < 50:
            lg = error_or_json(lg)
            if lg is None or len(lg) == 0:
                b += 1
                continue
            else:
                lg = lg[0]
            md = requests.get('https://americas.api.riotgames.com/lol/'
                              'match/v5/matches/' +
                              lg + '?api_key=' + self.api_key)
            md = error_or_json(md)
            if md is None:
                b += 1
                continue
            if md['info']['gameMode'] != 'CLASSIC':
                b += 1
            else:
                match_data.append(md)
                a += 1
                b += 1
        return None if len(match_data) == 0 else match_data


class Game:
    """A League game with 2 teams of 5 players.
    This class will literally just hold two lists with 5 player objects
    in each list.

    ===== Public Attributes =====
    ally: A list comprising of allied players
    enemy: A list comprising of enemy players
    man: the main player we are looking at
    namedict: dict with names and champions and info for players of each team.
    all_data: all the game data.
    game_id: The game id.
    api_key: gimme dat api key

    ===== Useful Methods =====
    count_smurf
    count_binters
    count_break
    count_veteran
    count_hotstreak
    
    ===== Other Methods =====
    get_kda: gets kda of a player
    get_win: tells whether 'ally' or 'enemy' won

    """

    # input game id and player summoner name.
    # 'teamId' 100 is blue, 200 is red
    # this class will go down the list of players, put each player object
    # in either the blue or red team
    def __init__(self, api_key: str, game_id: str, name: str, n: int) -> None:
        """Initializes a Game object"""
        self.api_key = api_key
        self.game_id = game_id
        # for now it's just the name, we'll assign the player object later.
        self.man = name.replace(' ', '')
        self.all_data = self.get_game_data()
        self.namedict = self.get_name_list(self.all_data)
        self.ally = []
        self.enemy = []
        for a in self.namedict['ally']:
            print(f'[Game]getting ally {a[0]}')
            print('############################')
            bal = self.get_player(a[0], n)
            if self.man == a[0]:
                print("[Game] that's the person we're investigating.")
                self.man = bal
            else:
                print(f'[Game] done checking {a[0]}, was not {self.man}')
            self.ally.append(bal)
        for c in self.namedict['enemy']:
            print(f'[Game]getting enemy {c[0]}')
            print('############################')
            self.enemy.append(self.get_player(c[0], n))
        if len(self.ally) == len(self.enemy) == 5 and \
                isinstance(self.man, Player):
            print(f'[Game]Successfully loaded game {self.game_id}')
        else:
            print(f'[Game]Something went WRONG loading game {self.game_id}')
            print('self.man is', type(self.man))
            print('length of self.ally is', len(self.ally))
            print('length of self.enemy is', len(self.enemy))

    # TOOLS
    def get_kda(self, name: str) -> Optional[Tuple]:
        """Returns (kills, death's, assists) or None for a person in the
        namedict.
        Gets KDA for the game...
        """
        for c in self.namedict['ally']:
            if c[0] == name:
                a = c[2]
                return a['kills'], a['deaths'], a['assists']
        for c in self.namedict['enemy']:
            if c[0] == name:
                a = c[2]
                return a['kills'], a['deaths'], a['assists']
        return None

    def get_win(self, team: str) -> Optional[bool]:
        """Returns whether the 'ally' or 'enemy' team won."""
        if team != 'ally' and team != 'enemy':
            return None
        return self.namedict[team][0][2]['win']

    # ACTUAL DATA COLLECTION METHODS
    def count_smurf(self) -> Tuple[int, int]:
        """Returns a tuple of (no. ally smurfs, no. enemy smurfs)
        Smurfs are defined as players with median kda > 4.5
        in their last few games
        """
        ally = 0
        enemy = 0
        for x in self.ally:
            b = []
        for i in range(0, len(x.match_info)):
            k, d, a = x.kda(x.match_info[i])
            d = max(d, 1)
            b.append((k + a) / d)
        if statistics.median(b) > 4.5:
            ally += 1
            print('[Game.SmurfCount] Ally Smurf: ' + x.name)
        for x in self.enemy:
            b = []
        for i in range(0, len(x.match_info)):
            k, d, a = x.kda(x.match_info[i])
            d = max(d, 1)
            b.append((k + a) / d)
        if statistics.median(b) > 4.5:
            enemy += 1
            print('[Game.SmurfCount] Enemy Smurf: ' + x.name)
        return ally, enemy

    def count_binters(self) -> Tuple[int, int]:
        """Counts the number of binters on each team, returns (ally, enemy)
        A binter is defined as someone with <35%
        winrate in their past few games."""
        ally = 0
        enemy = 0
        for x in self.ally:
            win = 0
            total = 0
            for i in range(0, len(x.match_info)):
                if x.win(x.match_info[i]):
                    win += 1
                total += 1
            if win / total < 0.35:
                print(f'[Game.binterCount]: found ally {x.name}')
                ally += 1
        for x in self.enemy:
            win = 0
            total = 0
            for i in range(0, len(x.match_info)):
                if x.win(x.match_info[i]):
                    win += 1
                total += 1
            if win / total < 0.35:
                print(f'[Game.binterCount]: found enemy {x.name}')
                enemy += 1
        return ally, enemy

    def count_break(self) -> Tuple[int, int]:
        """Finds people who went on a break. Returns (ally, enemy)
        Looks for people with a >20 day gap between two of their recent games.
        """
        ally = 0
        enemy = 0
        for x in self.ally:
            last = None
            for mach in x.match_info:
                curr = mach['info']['gameCreation']/1000
                if last is not None and last-curr > 1728000:
                    ally += 1
                    print(f'[Game.breakCount]: found ally {x.name}')
                    break
                last = curr
        for x in self.enemy:
            last = None
            for mach in x.match_info:
                curr = mach['info']['gameCreation']/1000
                if last is not None and last-curr > 1728000:
                    enemy += 1
                    print(f'[Game.breakCount]: found enemy {x.name}')
                    break
                last = curr
        return ally, enemy

    def count_veteran(self) -> Tuple[int, int]:
        """Finds number of hardstuck players on each team, returns Ally, Enemy
        See Player.is_veteran() for more info.
        """
        ally, enemy = 0, 0
        for x in self.ally:
            if x.is_veteran():
                print(f'[Game.veteranCount]: found ally {x.name}')
                ally += 1
        for x in self.enemy:
            if x.is_veteran():
                print(f'[Game.veteranCount]: found enemy {x.name}')
                enemy += 1
        return ally, enemy

    def count_hotstreak(self) -> Tuple[int, int]:
        """Finds number of hotstreaking players on each team. Returns A, E
        See Player.is_hotstreaking() or whatever for more info.
        """
        ally, enemy = 0, 0
        for x in self.ally:
            if x.is_hotstreak():
                print(f'[Game.hotstreakCount]: found ally {x.name}')
                ally += 1
        for x in self.enemy:
            if x.is_hotstreak():
                print(f'[Game.hotstreakCount]: found enemy {x.name}')
                enemy += 1
        return ally, enemy

    # INITIALIZER METHODS

    def get_game_data(self) -> Optional[Dict]:
        """Gets json data for a game, based on the Game ID.
        returns none if no game is found.
        """
        game = requests.get('https://americas.api.riotgames.com/lol/match/v5/'
                            'matches/' + self.game_id +
                            '?api_key=' + self.api_key)
        return error_or_json(game)

    def get_name_list(self, game_data: Dict) -> Dict:
        """Returns a dictionary where:
        'ally' corresponds to a list of allied summoners
        'enemy' corresponds to a list of enemies.
        The list contains tuples of (summonerName, championName, alldata)"""
        # self.name is the ally team
        # we just make two lists then assign them
        # info > participants > summonername
        # info > participants > championName also teamId
        retdict = {}
        list1 = []
        list2 = []
        for man in game_data['info']['participants']:
            tmp = (man['summonerName'].replace(' ', ''),
                   man['championName'], man)
            if man['teamId'] == 100:
                list1.append(tmp)
            else:
                list2.append(tmp)
        if self.man in list1:
            retdict['ally'] = list1
            retdict['enemy'] = list2
        else:
            retdict['ally'] = list2
            retdict['enemy'] = list1
        if len(retdict['ally']) == len(retdict['enemy']) == 5:
            print(f'[Game.namedict] Participants for {self.game_id} '
                  f'loaded correctly.')
        else:
            print(f'[Game.namedict] Participants for {self.game_id} '
                  f'loaded INCORRECTLY')

        return retdict

    def get_player(self, summoner_name, n):
        return Player(self.api_key, summoner_name, n)


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
