
import argparse
import datetime
import json
import pickle

import requests

PICKLE_FILE = 'games.p'
TEAMS_FILE = 'teams.json'

QUERY_CMD = 'query'
LOAD_CMD = 'load'
SAVE_CMD = 'save'


def main():
    args = _load_args()
    if args.command == QUERY_CMD:
        team = _find_team(args.team)
        games = _find_games(args.date, team['id'])
        if not games:
            exit(f'Unable to find game on {args.date} for team {args.team}')
        if len(games) > 1:
            exit(f'Unexpected error, found multiple games for {args.date}')
        print(games)
    else:
        # TODO - setup save/load and save some game data
        exit('not finished here yet...')


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
    url = 'https://statsapi.web.nhl.com/api/v1/schedule'
    params = {
        'date': day,
        'teamId': team_id,
        'hydrate': 'broadcasts(all)'
    }
    response = requests.get(url, params=params)
    data = response.json()
    dates = data.get('dates', [])
    if not dates:
        return []
    return [_find_game_details(x) for x in dates[0]['games']]


def _find_game_details(game):
    game_id = game['gamePk']
    url = f'https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live'
    response = requests.get(url)
    details = response.json()
    details['_status'] = details['gameData']['status']['detailedState'].lower()  # noqa:E501
    details['broadcasts'] = [
        x
        for x in game['broadcasts']
        if x['language'].lower() in ['en']
    ]
    return details


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
    parser = argparse.ArgumentParser()

    # config for shorthand date options
    date_format = '%Y-%m-%d'
    quick_dates = {
        'today': datetime.date.today().strftime(date_format),
        'tomorrow': (datetime.datetime.today() - datetime.timedelta(days=-1)).strftime(date_format),  # noqa:E501
        'yesterday': (datetime.datetime.today() - datetime.timedelta(days=1)).strftime(date_format)  # noqa:E501
    }
    quick_date_opts = '{' + ','.join(quick_dates.keys()) + '}'

    subparsers = parser.add_subparsers(dest='command')
    parser_query = subparsers.add_parser(QUERY_CMD)
    parser_save = subparsers.add_parser(SAVE_CMD)
    parser_load = subparsers.add_parser(LOAD_CMD)
    for each in [parser_save, parser_query]:
        each.add_argument(
            '--team',
            required=True,
            help='team search term partical match for name, location, or abbreviation')  # noqa: E501
        each.add_argument(
            '--date',
            required=False,
            default='today',
            help=f'YYYY-MM-DD specific date or one of {quick_date_opts}')
    parser_save.add_argument(
        '--name',
        required=True,
        help='Save raw game data with input name to test with later')
    parser_load.add_argument(
        '--name',
        required=False,
        help='Load raw game data with input name instead of querying')
    args = parser.parse_args()

    # handle user not submitting command
    if not args.command:
        parser.print_help()
        exit()

    # convert date arg to formatted string
    if args.date:
        if args.date in quick_dates.keys():
            args.date = quick_dates[args.date]
        else:
            try:
                datetime.datetime.strptime(args.date, date_format)
            except ValueError:
                exit(f'{args.date} not in format {date_format} or {quick_date_opts}')  # noqa:E501

    return args


if __name__ == '__main__':
    main()
