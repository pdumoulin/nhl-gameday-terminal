
import json
import pickle
import sys

PICKLE_FILE = 'games.p'
TEAMS_FILE = 'teams.json'


def main():
    term = sys.argv[1]
    team = _find_team(term)
    print(team)


def _find_team(term):
    term = term.lower()
    with open(TEAMS_FILE, 'r') as filename:
        data = filename.read()
    team_list = json.loads(data)
    teams = [
        x for x in team_list
        if term in x['name'].lower() or
        term in x['abbreviation'].lower() or
        term in x['shortName'].lower()
    ]
    if not teams:
        exit(f'Could not find team using search term "{term}"')
    elif len(teams) > 1:
        matches = ', '.join([x['name'] for x in teams])
        exit(f'Matched too many teams with search term "{term}" => {matches}')  # noqa:E501
    return teams[0]


def _find_games(day, team_id):
    pass


def _find_game_details(game):
    pass


def _save_game_data(name, data):
    games = pickle.load(open(PICKLE_FILE, 'rb'))
    if name in games:
        exit(f'Game named "{name}" already exists in saved data!')
    games[name] = data
    pickle.dump(games, open(PICKLE_FILE, 'wb'))


def _load_game_data(name):
    games = pickle.load(open(PICKLE_FILE, 'rb'))
    if name not in games:
        print('\n'.join([x for x in games.keys()]))
        if name:
            exit(f'Unable to find game named "{name}" in saved data!')
        else:
            exit()
    return games[name]


def _delete_game_data(name):
    games = pickle.load(open(PICKLE_FILE, 'rb'))
    if name not in games:
        exit(f'Unable to find game named "{name}" in saved data!')
    del games[name]
    pickle.dump(games, open(PICKLE_FILE, 'wb'))


def _load_args():
    pass


if __name__ == '__main__':
    main()
