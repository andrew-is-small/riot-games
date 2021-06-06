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
    match_info: list of game jsons for the past n SR matches.
    match_info_all: list of all game jsons for the past n matches

    === Useful Methods ===
    get_ranked_wr: float
    get_win_score: win streak/loss streak as a +/- int
    is_veteran: boolean
    is_hotstreak: boolean

    === Helper Methods ===
    kda: finds player's kda in a game from the json
    win: finds if a player won a game from the json
    """

    def __init__(self, api_key: str, name: str, n: int) -> None:
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
        self.match_info, self.match_info_all = \
            self.get_match_infos(self.sum_info['puuid'])
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
        if jason is None or jason == []:
            return None
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

    def get_win_score(self) -> Optional[int]:
        """Gets the players win or loss streak over all game modes.
        Returns a number representing the streak. + for win, - for loss."""
        if not self.match_info_all:
            return None
        score = 0
        initial_condition = self.win(self.match_info_all[0])
        for match in self.match_info_all:
            if self.win(match) == initial_condition:
                score += 1
        return score if initial_condition else -score

    def is_veteran(self) -> Optional[bool]:
        """Returns whether or not this player is a 'veteran'
        (aka hardstuck basically)"""
        if self.ranked_info is None:
            return None
        for i in range(0, len(self.ranked_info)):
            if self.ranked_info[i]['veteran']:
                return True
        return False

    def is_hotstreak(self) -> Optional[bool]:
        """Returns whether or not the player is hotstreaking(3+ game winstreak)
        """
        if self.ranked_info is None:
            return None
        for i in range(0, len(self.ranked_info)):
            if self.ranked_info[i]['hotStreak']:
                return True
        return False

    def get_avg_time_binting(self) -> Optional[float]:
        """Gets average % of time that the player has spent dead
        in their last n games. Gives the decimal value.
        """
        total = 0
        count = 0
        if self.match_info is None:
            return None
        for game in self.match_info:
            index = game['metadata']['participants'] \
                .index(self.sum_info['puuid'])
            sum_stats = game['info']['participants'][index]
            total += sum_stats['totalTimeSpentDead'] / sum_stats['timePlayed']
            count += 1
        return total / count if count != 0 else None

    def is_otp(self, champ: str) -> bool:
        """Returns whether or not >60% of their past n games have been on
        champ.
        """
        count = 0
        total = 0
        if self.match_info is None:
            return False
        for game in self.match_info:
            index = game['metadata']['participants'] \
                .index(self.sum_info['puuid'])
            sum_stats = game['info']['participants'][index]
            if sum_stats['championName'] == champ:
                count += 1
            total += 1
        print(f'[{self.name}.isOTP] played {champ} {count} times in the last'
              f' {total} games.')
        return True if total != 0 and count / total > 0.6 else False

    def is_4fun(self) -> Optional[bool]:
        """Returns whether >60% of their past n games were not
        Summoners rift games."""
        counter = 0
        total = 0
        if self.match_info_all is None:
            return None
        for match in self.match_info_all:
            if match['info']['gameMode'] != 'CLASSIC':
                counter += 1
            total += 1
        return True if total > 0 and counter / total > 0.6 else False

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

    def get_match_infos(self, puuid: str) -> Optional[Tuple[List, List]]:
        """Gets match information for the past n SR matches and past n matches.
        Returns tuple of SR matches, All matches
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
        all_match_data = []
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
                b = a['info']['gameMode'] if a is not None else 'None'
                print(f'[{self.name}]{gameid} was not a summoners rift game,'
                      f'({b})')
            if a is not None and len(all_match_data) < self.n:
                all_match_data.append(a)
            if counterc == self.n:
                break
        if counterc < self.n:
            print(f'[Player]Warning: {self.n} games requested, only found '
                  f'{counterc} games for {self.name}')
        return None if len(match_data) == 0 else match_data, all_match_data

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
        """Initializes a Game object.
        Name is the 'main' player you wanna look at in the game."""
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
            print('self.man is', type(self.man), '(should be a <Player> obj)')
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

    def get_main_namedict(self) -> Optional[Tuple[str, str, Any]]:
        """Gets the main player's tuple from the namedict"""
        for i in self.namedict['ally']:
            if i[0] == self.man.name:
                return i
        return None

    def get_admd(self, team: str) -> List[Dict]:
        """Gets list of tuples for 'attack', 'defense', 'magic', 'difficulty'"""
        # inefficient to send request every time but requests won't be
        # frequent, it's whatever.
        champ_data = get_champ_info()['data']
        ret_lst = []
        for player in self.namedict[team]:
            champ_played = player[1]
            if champ_played in champ_data:
                ret_lst.append(champ_data[champ_played]['info'])
        return ret_lst

    def get_sum_from_admd(self, what: str) -> \
            Tuple[Optional[int], Optional[int]]:
        """Used to get a sum of values for attack/defense, etc. from
        the output of the get_admd function. Returns A, E tuple.
        """
        al = self.get_admd('ally')
        en = self.get_admd('enemy')
        ret_tuple = []
        if not al or what not in al[0]:
            ret_tuple.append(None)
        else:
            total_a = 0
            for a in al:
                total_a += a[what]
            ret_tuple.append(total_a)
        if not en or what not in en[0]:
            ret_tuple.append(None)
        else:
            total_e = 0
            for a in en:
                total_e += a[what]
            ret_tuple.append(total_e)
        return tuple(ret_tuple)

    # ACTUAL DATA COLLECTION METHODS
    def get_wr_list(self) -> Tuple[List, List]:
        """Returns a tuple of allied WR, enemy WR."""
        a_lst = []
        e_lst = []
        for i in self.ally:
            if i.get_ranked_wr() is not None:
                a_lst.append(i.get_ranked_wr())
        for i in self.enemy:
            if i.get_ranked_wr() is not None:
                e_lst.append(i.get_ranked_wr())
        return a_lst, e_lst

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

    def get_highest_median_kda(self) -> Tuple[int, int]:
        """Highest median kda for ally, enemy
        """
        ally = 0
        enemy = 0
        for x in self.ally:
            b = []
        for i in range(0, len(x.match_info)):
            k, d, a = x.kda(x.match_info[i])
            d = max(d, 1)
            b.append((k + a) / d)
        if statistics.median(b) > ally:
            ally = statistics.median(b)
        for x in self.enemy:
            b = []
        for i in range(0, len(x.match_info)):
            k, d, a = x.kda(x.match_info[i])
            d = max(d, 1)
            b.append((k + a) / d)
        if statistics.median(b) > enemy:
            enemy = statistics.median(b)
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
        """Finds the longest break taken btwn two consecutive games by a
        member on either team.
        Returns (ally, enemy)
        """
        ally = 0
        enemy = 0
        for x in self.ally:
            last = None
            for mach in x.match_info:
                curr = mach['info']['gameCreation'] / 1000
                if last is not None and last - curr > ally:
                    ally = last - curr
                    # print(f'[Game.breakCount]: found ally {x.name}')
                    break
                last = curr
        for x in self.enemy:
            last = None
            for mach in x.match_info:
                curr = mach['info']['gameCreation'] / 1000
                if last is not None and last - curr > enemy:
                    enemy = last - curr
                    # print(f'[Game.breakCount]: found enemy {x.name}')
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
        The list contains tuples of (summonerName, championName, alldata)
        Precondition: Self.man is a string at this point.
        """
        # self.name is the ally team
        # we just make two lists then assign them
        # info > participants > summonername
        # info > participants > championName also teamId
        retdict = {}
        list1 = []
        list2 = []
        main_guy = ''
        for man in game_data['info']['participants']:
            naeme = man['summonerName'].replace(' ', '')
            tmp = (naeme,
                   man['championName'], man)
            if naeme == self.man:
                main_guy = tmp
            if man['teamId'] == 100:
                list1.append(tmp)
            else:
                list2.append(tmp)
        if main_guy in list1:
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

    def get_player(self, summoner_name: str, n: int) -> Player:
        """Gets a player object based on their summoner name"""
        if summoner_name in player_objects and \
                player_objects[summoner_name].n == n:
            return player_objects[summoner_name]
        guy = Player(self.api_key, summoner_name, n)
        player_objects[summoner_name] = guy
        return guy


class GameAnalysis:
    """A Class. What does it do?

    It will assemble all the necessary stats for a game.
    We will feed it a game id, and a player, and it will give us the stats.
    """

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    # THE BIG METHOD
    def analyze_game(self, game: Tuple[str, str], n: int) -> Dict:
        """Analyzes game. Pass in a tuple gameid, summoner name"""
        ret_dict = {}
        a = Game(self.api_key, game[0], game[1], n)
        # analyze game here
        # I'M LISTING OFF A LOT OF THINGS THAT WILL GIVE US THE STATS.
        # I'LL PUT EM IN A DICTIONARY

        # gameid
        ret_dict['gameid'] = game[0]
        # player
        ret_dict['player'] = game[1]
        ret_dict['champion'] = a.get_main_namedict()[1]
        # player_wr
        ret_dict['player_wr'] = a.man.get_ranked_wr()
        ret_dict['t_bint'] = a.man.get_avg_time_binting()
        ret_dict['is_main_h'] = a.man.is_otp(a.get_main_namedict()[1])
        ret_dict['smurf_count_a'], ret_dict['smurf_count_e'] = a.count_smurf()
        ret_dict['hotstreak_count_a'], ret_dict['hotstreak_count_e'] = \
            a.count_hotstreak()
        # TODO UPDATE 4FUN FOR ALLY AND ENEMY TO COUNT 4FUN
        ret_dict['4fun'] = a.man.is_4fun()
        ret_dict['veteran_count_a'], ret_dict['veteran_count_e'] = \
            a.count_veteran()
        ret_dict['inters_count_a'], ret_dict['inters_count_e'] = \
            a.count_binters()
        ret_dict['break_count_a'], ret_dict['break_count_e'] = a.count_break()
        # attack sum a and e
        ret_dict['a_sum_a'], ret_dict['a_sum_e'] = a.get_sum_from_admd('attack')
        ret_dict['d_sum_a'], ret_dict['d_sum_e'] = \
            a.get_sum_from_admd('defense')
        ret_dict['m_sum_a'], ret_dict['m_sum_e'] = a.get_sum_from_admd('magic')
        wr_a, wr_e = a.get_wr_list()
        if wr_a:
            ret_dict['wr_med_a'] = statistics.median(wr_a)
            ret_dict['wr_min_a'] = min(wr_a)
            ret_dict['wr_max_a'] = max(wr_a)
        else:
            ret_dict['wr_med_a'], ret_dict['wr_min_a'], ret_dict['wr_max_a'] = \
                None, None,
        if wr_e:
            ret_dict['wr_med_e'] = statistics.median(wr_e)
            ret_dict['wr_min_e'] = min(wr_e)
            ret_dict['wr_max_e'] = max(wr_e)
        else:
            ret_dict['wr_med_e'], ret_dict['wr_min_e'], ret_dict['wr_max_e'] = \
                None, None, None
        ret_dict['max_med_kd_a'], ret_dict['max_med_kd_e'] = \
            a.get_highest_median_kda()

        return ret_dict


# GOOD METHODS
def error_or_json(thing: requests.Response) -> Optional[Union[Dict, List]]:
    if not thing.ok:
        print('Resource not found, code {code}'
              .format(code=thing.status_code))
        return None
    return thing.json()


def get_champ_info() -> Dict:
    # TODO REMEMBER TO CHANGE VERSION NUMBER
    version_number = '11.11.1'
    a = requests.get('http://ddragon.leagueoflegends.com/cd'
                     'n/' + version_number + '/data/en_US/champion.json')
    return a.json()


def load_config(config_file) -> Dict:
    """Right now, it just returns the API key. Idk what else to do with it"""
    with open(config_file, 'r') as file:
        config = json.load(file)
        return config
