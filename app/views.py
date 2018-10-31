import os
import binascii
import time

from flask import request, g, jsonify, abort, render_template

from app import (app, log_app, get_current_team_id, ajax_response, acl_check, storage)


PENALTY_SCORE_BY_HINT_IN_SECONDS = 15 * 60
PENALTY_SCORE_BY_INVALID_ANSWER_IN_SECONDS = 10 * 60


@app.before_request
def before_request():
    g.request_uid = binascii.b2a_hex(os.urandom(20))
    g.request_start_time = time.time()
    log_app("request\t%s\t%s\t%s" % (request.url, request.method, get_current_team_id()))


@app.after_request
def after_request(response):
    response_time = time.time() - g.request_start_time
    log_app("response\t%s\t%s" % (response.status_code, response_time))
    log_app("for_splunk response-time-stat\ttime=%s,code=%s,path=%s" % (response_time, response.status_code,
                                                                        request.path))
    return response


@acl_check('games')
@app.route('/', methods=['GET'])
def games():
    games = storage.fetch_games()
    return render_template('index.html', games=games)


@acl_check('tasks')
@app.route('/<int:game_id>/tasks', methods=['GET'])
def tasks(game_id: int):
    # @todo show only open tasks for current team
    tasks = storage.fetch_tasks(game_id)
    return render_template('tasks.html', tasks=tasks, game_id=game_id)


@acl_check('tasks')
@app.route('/<int:game_id>/tasks/<int:task_id>', methods=['GET'])
def task_view(game_id: int, task_id: int):
    task = storage.fetch_task(game_id, task_id)
    if not task:
        abort(404)
    return render_template('task_view.html', task=task, game_id=game_id, task_id=task_id,
                           hints=storage.fetch_hints(task_id))


@acl_check('tasks')
@app.route('/<int:game_id>/tasks/<int:task_id>', methods=['POST'])
def task_resolve(game_id: int, task_id: int):
    task = storage.fetch_task(game_id, task_id)
    if not task:
        abort(404)
    if storage.team_task_already_complete(get_current_team_id(), task_id):
        log_app('already complete this task')
        abort(400)

    answer = request.form.get('answer', '', type=str)
    if task['answer'].lower() != answer.lower():
        storage.add_penalty_score(get_current_team_id(), PENALTY_SCORE_BY_INVALID_ANSWER_IN_SECONDS)
        return jsonify(ajax_response(False))
    else:
        storage.task_resolve(get_current_team_id(), task_id)
        return jsonify(ajax_response(True))


@acl_check('hints')
@app.route('/<int:game_id>/tasks/<int:task_id>/hints/<int:hint_id>', methods=['GET'])
def hint_view(game_id: int, task_id: int, hint_id: int):
    hint = storage.fetch_hint(game_id, task_id, hint_id)
    if not hint:
        abort(404)
    storage.add_penalty_score(get_current_team_id(), PENALTY_SCORE_BY_HINT_IN_SECONDS)
    return render_template('hint_view.html', message=hint['title'])


@acl_check('scoring')
@app.route('/<int:game_id>/scoring', methods=['GET'])
def scoring(game_id: int):
    game = storage.fetch_game(game_id)
    if not game:
        abort(404)
    score_table = storage.score_table(game_id, game['start_date'])
    return render_template('scoring.html', score_table=score_table, game_id=game_id)

