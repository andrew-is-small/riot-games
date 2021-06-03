import main
import datetime


def cock_a_bitch(md):
    gmode = {'CLASSIC': 'Summoner\'s Rift (Normals)',
             'ARAM': 'Howling Abyss (ARAM)',
             'NEXUSBLITZ': 'Nexus Blitz'}
    gtime = md['info']['gameDuration']
    time_lol = str(datetime.timedelta(milliseconds=gtime))
    print('Gamemode: ' + gmode[md['info']['gameMode']])
    print('Duration: ' + time_lol)


cfg = main.load_config('res/config.json')
API_KEY = cfg['api_key']

andrew = main.Player(API_KEY, 'TLDababy', 10)

for i in andrew.match_info:
    cock_a_bitch(i)
