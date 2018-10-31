import operator
from datetime import datetime, timedelta

# @todo add fixture
from math import ceil
from typing import Optional


class Storage:
    # @todo persistence

    def __init__(self):
        self.games = [
            dict(id=1, start_date=datetime.utcnow() - timedelta(days=2), title='Game title 1'),
            dict(id=2, start_date=datetime.utcnow() - timedelta(days=1), title='Game title 2'),
        ]

        self.locations = [
            dict(id=1, title='Location title 1', coordinates='12.345X12.3132'),
        ]

        self.teams = [
            dict(id=1, penalty_seconds=0, title='Team 1'),
            dict(id=2, penalty_seconds=0, title='Team 2'),
            dict(id=3, penalty_seconds=0, title='Team 3'),
            dict(id=4, penalty_seconds=0, title='Team 4'),
            dict(id=5, penalty_seconds=0, title='Team 5'),
            dict(id=6, penalty_seconds=10, title='Team 6'),
            dict(id=7, penalty_seconds=0, title='Team 7'),
            dict(id=8, penalty_seconds=0, title='Team 8'),
            dict(id=9, penalty_seconds=0, title='Team 9'),
            dict(id=10, penalty_seconds=0, title='Team 10'),
        ]

        self.tasks = [
            dict(id=1, question='Q1', answer='A1', location_id=1, game_id=1, img_link=None),
            dict(id=2, question='Q2', answer='A2', location_id=1, game_id=1, img_link='https://google.com/favicon.ico'),
            dict(id=3, question='Q3', answer='A3', location_id=1, game_id=2, img_link='https://google.com/favicon.ico'),
        ]

        # @todo use set for it
        self.teams_tasks = [
            dict(team_id=5, task_id=1, date_complete=datetime.utcnow()),
            dict(team_id=6, task_id=1, date_complete=datetime.utcnow()),
            dict(team_id=6, task_id=3, date_complete=datetime.utcnow()),
        ]

        self.tasks_hints = [
            dict(id=1, task_id=1, title='Hint message 1'),
            dict(id=2, task_id=1, title='Hint message 2'),
            dict(id=3, task_id=1, title='Hint message 3'),
            dict(id=4, task_id=2, title='Hint message 1'),
            dict(id=5, task_id=2, title='Hint message 2'),
            dict(id=6, task_id=2, title='Hint message 3'),
        ]

    def fetch_games(self) -> list:
        return self.games

    def fetch_game(self, game_id:int) -> Optional[dict]:
        game = list(filter(lambda x: x['id'] == game_id, self.games))
        if not game:
            return None
        return game[0]

    def fetch_tasks(self, game_id:int) -> list:
        return list(filter(lambda x: x['game_id'] == game_id, self.tasks))

    def fetch_task(self, game_id:int, task_id:int) -> Optional[dict]:
        task = list(filter(lambda x: x['game_id'] == game_id and x['id'] == task_id, self.tasks))
        if not task:
            return None
        return task[0]

    def fetch_hint(self, game_id:int, task_id:int, hint_id:int) -> Optional[dict]:
        task = self.fetch_task(game_id, task_id)
        if not task:
            return None
        hints = list(filter(lambda x: x['task_id'] == task_id and x['id'] == hint_id, self.tasks_hints))
        if not hints:
            return None
        return hints[0]

    def add_penalty_score(self, team_id: int, score: int):
        index = [i for i, v in enumerate(self.teams) if v['id'] == team_id][0]
        self.teams[index]['penalty_seconds'] += score

    def team_task_already_complete(self, team_id: int, task_id: int) -> bool:
        try:
            answer = list(filter(lambda x: x['team_id'] == team_id and x['task_id'] == task_id, self.teams_tasks))[0]
            return True
        except IndexError:
            return False

    def task_resolve(self, team_id: int, task_id: int):
        self.teams_tasks.append(dict(team_id=team_id, task_id=task_id, date_complete=datetime.utcnow()))

    def fetch_resolved_tasks(self, team_id: int, valid_task_ids: set) -> list:
        return list(filter(lambda x: x['team_id'] == team_id and x['task_id'] in valid_task_ids, self.teams_tasks))

    def compute_task_score(self, start_dt: datetime, end_dt: datetime) -> int:
        diff_dt = end_dt - start_dt
        return ceil(diff_dt.total_seconds())

    def score_table(self, game_id: int, game_start_time: datetime) -> list:
        all_tasks_by_game = self.fetch_tasks(game_id)
        all_valid_task_ids = set([i['id'] for i in all_tasks_by_game])

        out = []
        for team in self.teams:
            resolved_tasks = self.fetch_resolved_tasks(team['id'], all_valid_task_ids)
            resolved_task_score = sum([self.compute_task_score(game_start_time, task['date_complete']) for task in resolved_tasks])
            out.append(dict(team_title=team['title'], penalty_score_seconds=team['penalty_seconds'],
                            resolved_task_count=len(resolved_tasks), resolved_task_score=resolved_task_score,
                            total_score=resolved_task_score + team['penalty_seconds']))

        return sorted(out, key=lambda x: (x['resolved_task_count'], -x['total_score']), reverse=True)
