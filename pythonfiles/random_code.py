import main
import datetime
import time

cfg = main.load_config('res/config.json')
API_KEY = cfg['api_key']


def cock_a_bitch(md):
    gmode = {'CLASSIC': 'Summoner\'s Rift (Normals)',
             'ARAM': 'Howling Abyss (ARAM)',
             'NEXUSBLITZ': 'Nexus Blitz'}
    gtime = md['info']['gameDuration']
    time_lol = str(datetime.timedelta(milliseconds=gtime))
    print('Gamemode: ' + gmode[md['info']['gameMode']])
    print('Duration: ' + time_lol)


def cock1():
    andrew = main.Player(API_KEY, 'troll125', 10)

    for i in andrew.match_info:
        cock_a_bitch(i)


def cock1_1():
    ohm = main.Player(API_KEY, 'TL Dababy', 1)
    for i in ohm.match_info:
        print(i['metadata']['matchId'])
        print(i['info']['gameMode'])


def cock2():
    for _ in range(0, 10):
        time.sleep(1)
        print('dick')


def cock3():
    game_id = 'NA1_3931766940'
    cock = main.Game(API_KEY, game_id, 'TL DaBaby', 1)
    print('=== ALLIES ===')
    print('Win?', cock.get_win('ally'))
    for x in cock.namedict['ally']:
        k, d, a = cock.get_kda(x[0])
        print(x[0], 'played', x[1], ':', str(k) + '/' + str(d) + '/'
              + str(a))
    print('=== ENEMIES ===')
    for x in cock.namedict['enemy']:
        k, d, a = cock.get_kda(x[0])
        print(x[0], 'played', x[1], 'went', str(k) + '/' + str(d) + '/'
              + str(a))


cock3()
