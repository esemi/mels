from functools import wraps
import logging
import os
import sys

from flask import Flask, request, g, abort

from app.storage import Storage


SERVICE_PATH = os.path.join(os.path.dirname(__file__), os.pardir)
APP_PATH = os.path.abspath(SERVICE_PATH)


def __setup_logging(app_inst):
    file_handler = logging.StreamHandler(sys.stdout)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    app_inst.logger.addHandler(file_handler)
    if app_inst.config['DEBUG']:
        app_inst.logger.setLevel(logging.DEBUG)
    else:
        app_inst.logger.setLevel(logging.INFO)


def __setup_config(app_inst):
    # @todo add configs by env

    try:
        import settings as local_config
        app_inst.config.from_object(local_config)
    except ImportError:
        pass


def log_app(message):
    try:
        uid = g.request_uid
    except AttributeError:
        uid = ''
    try:
        app.logger.info("%s\t%s", uid, message)
    except RuntimeError:
        pass


def get_current_team_id():
    try:
        return app.config['DEBUG_USER_TEAM_ID']
    except KeyError:
        # @todo release
        return request.headers.get("X-Mels-User")


def acl_check(resource_name):
    def decorated(f):
        @wraps(f)
        def _decorated(*args, **kwargs):
            team_id = get_current_team_id()
            if not team_id:
                log_app('ACL check failure: not auth team %s' % team_id)
                abort(403)

            # @todo release
            is_allow = True

            if not is_allow:
                log_app('ACL check failure %s %s' % (user_id, resource_name))
                abort(403)
            return f(*args, **kwargs)

        return _decorated
    return decorated


def ajax_response(success, errors=None, data=None) -> dict:
    if not errors:
        errors = list()
    if not data:
        data = dict()
    return {'success': success, 'errors': errors, 'data': data}


storage = Storage()

app = Flask(__name__)
__setup_config(app)
__setup_logging(app)

from app import views
