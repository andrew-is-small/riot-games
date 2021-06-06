import main

# PlatypusOfCanada's player info from
# https://na1.api.riotgames.com/lol/league/v4/entries/
# by-summoner/sumId?api_key=apiKey
cfg = main.load_config('res/config.json')
API_KEY = cfg['api_key']

regular_dict = [{'leagueId': '1c6c365f-e784-4ef4-9b53-98f5cf47fa7c',
                 'queueType': 'RANKED_SOLO_5x5',
                 'tier': 'BRONZE',
                 'rank': 'I',
                 'summonerId': 'lWvclwcJ92XHvnfk9sv7LUqXFoiJtJovpqEysbc8NMBcEbU',
                 'summonerName': 'PlatypusOfCanada',
                 'leaguePoints': 53,
                 'wins': 7,
                 'losses': 6,
                 'veteran': False,
                 'inactive': False,
                 'freshBlood': False,
                 'hotStreak': True},
                {'leagueId': '68a20f0b-501b-439c-a4af-91b5a3d2a05f',
                 'queueType': 'RANKED_FLEX_SR',
                 'tier': 'BRONZE',
                 'rank': 'I',
                 'summonerId': 'lWvclwcJ92XHvnfk9sv7LUqXFoiJtJovpqEysbc8NMBcEbU',
                 'summonerName': 'PlatypusOfCanada',
                 'leaguePoints': 82,
                 'wins': 4,
                 'losses': 6,
                 'veteran': False,
                 'inactive': False,
                 'freshBlood': False,
                 'hotStreak': False}]
# same as above but with no ranked games played
# TODO maybe look at nongkrekacid's history for actual data
regular_dict_2 = [{'leagueId': '1c6c365f-e784-4ef4-9b53-98f5cf47fa7c',
                   'queueType': 'RANKED_SOLO_5x5',
                   'tier': 'BRONZE',
                   'rank': 'I',
                   'summonerId': 'lWvclwcJ92XHvnfk9sv7LUqXFoiJtJovpqEysbc8NMBcEbU',
                   'summonerName': 'PlatypusOfCanada',
                   'leaguePoints': 53,
                   'wins': 0,
                   'losses': 0,
                   'veteran': False,
                   'inactive': False,
                   'freshBlood': False,
                   'hotStreak': True},
                  {'leagueId': '68a20f0b-501b-439c-a4af-91b5a3d2a05f',
                   'queueType': 'RANKED_FLEX_SR',
                   'tier': 'BRONZE',
                   'rank': 'I',
                   'summonerId': 'lWvclwcJ92XHvnfk9sv7LUqXFoiJtJovpqEysbc8NMBcEbU',
                   'summonerName': 'PlatypusOfCanada',
                   'leaguePoints': 82,
                   'wins': 4,
                   'losses': 6,
                   'veteran': False,
                   'inactive': False,
                   'freshBlood': False,
                   'hotStreak': False}]
# same as regular_dict
regular_dict_3 = [{'leagueId': '1c6c365f-e784-4ef4-9b53-98f5cf47fa7c',
                   'queueType': 'RANKED_SOLO_5x5',
                   'tier': 'BRONZE',
                   'rank': 'I',
                   'summonerId': 'lWvclwcJ92XHvnfk9sv7LUqXFoiJtJovpqEysbc8NMBcEbU',
                   'summonerName': 'PlatypusOfCanada',
                   'leaguePoints': 53,
                   'wins': 0,
                   'losses': 0,
                   'veteran': False,
                   'inactive': False,
                   'freshBlood': False,
                   'hotStreak': True},
                  {'leagueId': '68a20f0b-501b-439c-a4af-91b5a3d2a05f',
                   'queueType': 'RANKED_FLEX_SR',
                   'tier': 'BRONZE',
                   'rank': 'I',
                   'summonerId': 'lWvclwcJ92XHvnfk9sv7LUqXFoiJtJovpqEysbc8NMBcEbU',
                   'summonerName': 'PlatypusOfCanada',
                   'leaguePoints': 82,
                   'wins': 0,
                   'losses': 0,
                   'veteran': False,
                   'inactive': False,
                   'freshBlood': False,
                   'hotStreak': False}]


def test_win_score():
    ohm = main.Player(API_KEY, 'TL DaBaby', 5)
    assert len(ohm.match_info_all) == 5
    print(ohm.get_win_score())
    assert isinstance(ohm.get_win_score(), int)


def tezt_all():
    import pytest
    pytest.main(['main_test.py', '-rx'])


tezt_all()
