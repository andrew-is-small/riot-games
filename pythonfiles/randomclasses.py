import csv

GAME_CSV = 'games3.csv'


def write_games(games):
    # games is a list of tuples for gameid, whatever
    file = open(GAME_CSV, 'a', newline='', encoding='UTF-8')
    writist = csv.writer(file, lineterminator='\n')
    for row in games:
        # row is gonna be a tuple
        writist.writerow(list(row))
    file.close()
