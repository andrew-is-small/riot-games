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
    print(ohm.win(ohm.match_info[0]))
    


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

def recent_win_rate():
    ally = ""
    enemy = ""
    game_id = 'NA1_3931766940'
    gong = main.Game(API_KEY, game_id, 'TL DaBaby', 6)
    for x in gong.ally:
        win = 0
        total = 0
        for i in range(0,len(x.match_info)):
            if x.win(x.match_info[i]):
                win += 1
            total +=1
        if win/total < 0.35:
            ally = ally + x.name + " "
    for x in gong.enemy:
        win = 0
        total = 0
        for i in range(0,len(x.match_info)):
            if x.win(x.match_info[i]):
                win += 1
            total +=1
        if win/total < 0.35:
            enemy = enemy + x.name + " "
    print('ally bintists: ' + ally + ' ')
    print('enemy bintists: ' + enemy+ ' ')


def win_score():
    #when we implement match infos for all rounds use this instead
    ally = ""
    enemy = ""
    game_id = 'NA1_3931766940'
    gong = main.Game(API_KEY, game_id, 'TL DaBaby', 3)
    for x in gong.ally:
        score = 0
        a = x.win(x.match_info[0])
        for i in range(0,len(x.match_info)):
            if x.win(x.match_info[i]) == x.win(x.match_info[0]):
                score += 1
        if not a:
            score = -score
        if abs(score) > 1:
            ally = ally + x.name + " " + str(score) + " "
    for x in gong.enemy:
        score = 0
        a = x.win(x.match_info[0])
        for i in range(0,len(x.match_info)):
            if x.win(x.match_info[i]) == x.win(x.match_info[0]):
                score += 1
        if not a:
            score = -score
        if abs(score) > 1:
            enemy = enemy + x.name + " " + str(score) + " "
    print('ally scores: ' + ally + ' ')
    print('enemy scores: ' + enemy + ' ')


def break_count():
    #when we implement match infos for all rounds use this instead
    ally = ""
    enemy = ""
    game_id = 'NA1_3931766940'
    gong = main.Game(API_KEY, game_id, 'TL DaBaby', 1)
    for x in gong.ally:
        for i in range(0,len(x.match_info)):
            if time.time() - (x.match_info[i]['info']['gameCreation'])/1000 > 1728000:
                ally = ally + x.name + " "
    for x in gong.enemy:
        for i in range(0,len(x.match_info)):
            if time.time() - (x.match_info[i]['info']['gameCreation'])/1000 > 1728000:
                enemy = enemy + x.name + " "
    print('ally gongagisntsts: ' + ally + ' ')
    print('eneym gongoasgnseitststss: ' + enemy+ ' ')
    
def veteran_count():
    #when we implement match infos for all rounds use this instead
    ally = ""
    enemy = ""
    game_id = 'NA1_3931766940'
    gong = main.Game(API_KEY, game_id, 'TL DaBaby', 1)
    for x in gong.ally:
        c = False
        for i in range(0,len(x.ranked_info)):
            if x.ranked_info[i]['veteran']:
                c = True
        if c:    
            ally = ally + x.name + " "
    for x in gong.enemy:
        c = False
        for i in range(0,len(x.ranked_info)):
            if x.ranked_info[i]['veteran']:
                c = True
        if c:    
            enemy = enemy + x.name + " "
    print('ally gong hardstuck: ' + ally + ' ')
    print('eneym gong hardstuck: ' + enemy+ ' ')
    
def hotstreak_count():
    #when we implement match infos for all rounds use this instead
    ally = ""
    enemy = ""
    game_id = 'NA1_3931766940'
    gong = main.Game(API_KEY, game_id, 'TL DaBaby', 1)
    for x in gong.ally:
        c = False
        for i in range(0,len(x.ranked_info)):
            if x.ranked_info[i]['hotStreak']:
                c = True
        if c:    
            ally = ally + x.name + " "
    for x in gong.enemy:
        c = False
        for i in range(0,len(x.ranked_info)):
            if x.ranked_info[i]['hotStreak']:
                c = True
        if c:    
            enemy = enemy + x.name + " "
    print('ally gong hotstreak: ' + ally + ' ')
    print('eneym gong hotstreak: ' + enemy+ ' ')

win_score()