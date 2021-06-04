import main
import datetime
import time
import statistics

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
    print(ohm.kda(ohm.match_info[0]))
    


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

def smurf_count():
    ally = 0
    enemy = 0
    game_id = 'NA1_3931766940'
    gong = main.Game(API_KEY, game_id, 'TL DaBaby', 5)
    for x in gong.ally:
        b = []
        for i in range(0,len(x.match_info)):
            k, d, a = x.kda(x.match_info[i])
            d = max(d,1)
            b.append((k+a)/d)
        if statistics.median(b) > 4.5:
            ally += 1
            print('this man is the gongeet' + x.name)
    for x in gong.enemy:
        b = []
        for i in range(0,len(x.match_info)):
            k, d, a = x.kda(x.match_info[i])
            d = max(d,1)
            b.append((k+a)/d)
        if statistics.median(b) > 4.5:
            enemy += 1
            print('this man is the gongeet' + x.name)
    print(ally)
    print(enemy)

smurf_count()