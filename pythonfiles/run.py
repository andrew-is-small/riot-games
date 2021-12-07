import main
import csv
import pandas as pd

# ALREADY RUN
# TODO literally read the csv file and get the gameid column...
df = pd.read_csv('data.csv')
SEEN = df['gameid'].tolist()
# continue this later

VARIABLES = ['gameid', 'player', 'champion', 'ally_win', 'player_wr', 't_bint', 'is_main_h', 'mastery_points',
             'smurf_count_a', 'smurf_count_e', 'hotstreak_count_a', 'hotstreak_count_e', '4fun', 'veteran_count_a',
             'veteran_count_e', 'inters_count_a', 'inters_count_e', 'break_count_a', 'break_count_e', 'a_sum_a',
             'a_sum_e', 'd_sum_a', 'd_sum_e', 'm_sum_a', 'm_sum_e', 'wr_med_a', 'wr_min_a', 'wr_max_a', 'wr_med_e',
             'wr_min_e', 'wr_max_e', 'max_med_kd_a', 'max_med_kd_e', '4fun_a', '4fun_e']

cfg = main.load_config('res/config.json')
API_KEY = cfg['api_key']


def dict_to_list(dic):
    """Converts return from GameAnalysis to a list, making sure everything is in the right column."""
    ret_l = [None] * len(VARIABLES)
    for i in range(0, len(VARIABLES)):
        if VARIABLES[i] in dic:
            ret_l[i] = dic[VARIABLES[i]]

    return ret_l


def write_to_csv(lst):
    with open('data.csv', 'a', newline='') as file:
        writist = csv.writer(file, lineterminator='\n')
        writist.writerow(lst)


def run(game_list):
    """Runs the entire thing. gong is a list of (gameid, player) tuples"""
    print(f'about to check {len(game_list)} games')
    seen_lst = []
    counter = 0
    seen = 0
    error_1 = 0
    error_2 = 0
    error_3 = 0
    for game in game_list:
        if game[0] in SEEN or game[0] in seen_lst:
            print('already seen', game[0])
            seen += 1
            continue
        seen_lst.append(game[0])
        # game is a tuple
        try:
            analysis = main.GameAnalysis(API_KEY)
            dic = analysis.analyze_game(game, 5)
            print(f'Entered {len(game_list)} games, already saw {seen}, recorded {counter}.')
            print(f'Random errors: {error_1}')
            print(f'Loading YouAreDumbOrSomethingError: {error_2}')
            print(f'Bad Player Errors: {error_3}')
            print('\n\n\n')
            lst = dict_to_list(dic)
            write_to_csv(lst)
            counter += 1
        except main.YouAreDumbOrSomethingError:
            error_2 += 1
            continue
        except main.BadPlayerError:
            error_3 += 1
        except PermissionError:
            print("bruh close the csv what's wrong with you")
            break
        except:
            error_1 += 1
            print('Something went wrong.\n\n\n')
    print(f'Entered {len(game_list)} games, already saw {seen}, recorded {counter}.')
    print(f'Random errors: {error_1}')
    print(f'Loading YouAreDumbOrSomethingError: {error_2}')


backup = [('NA1_3938838278', 'Blackbeard178'), ('NA1_3938822863', 'Blackbeard178'),
          ('NA1_3938717861', 'Blackbeard178'), ('NA1_3934823346', 'Blackbeard178'), ('NA1_3934677077', 'Blackbeard178')]


# Script to get games. We will load only the first 1000 games of the csv, and manually restart the process.

# TODO use games[], clear games[], change randomclasses[], get new api key[]j, start getting data again
csv_to_write_to = 'games2.csv'
to_run = []
a = pd.read_csv(csv_to_write_to)
a = a.loc[:1000, :]
for index, row in a.iterrows():
    to_run.append((str(row['gameid']), str(row['player'])))
print(f'Loaded {len(to_run)} games')
run(to_run)
