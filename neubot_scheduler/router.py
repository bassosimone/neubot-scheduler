#
# This file is part of Neubot <https://www.neubot.org/>.
#
# Neubot is free software. See AUTHORS and LICENSE for more
# information on the copying conditions.
#

""" Requests router """

import cgi
import json

from .backend import config_manager
from .backend import data_manager
from .backend import log_manager
from .backend import runner
from .backend import state_manager
from .backend import specs_manager

from . import http

def api_(connection, _):
    """ Implements /api/ API """
    connection.write(http.writer.compose_response("200", "Ok", {
        "Content-Type": "application/json",
    }, json.dumps(list(connection.server.routes.keys()))))

def api_config(connection, request):
    """ Implements /api/config API """

    query = ""
    index = request.url.find("?")
    if index >= 0:
        query = request.url[index + 1:]

    dictionary = cgi.parse_qs(query)
    if "labels" in dictionary and int(dictionary["labels"][0]):
        config_manager.get().get_config(connection, True)
    elif request.method == "POST":
        incoming = json.loads(request.body_as_string("utf-8"))
        config_manager.get().set_config(connection, incoming)
    else:
        config_manager.get().get_config(connection, False)

def api_data(connection, request):
    """ Implements /api/data API """

    query = ""
    index = request.url.find("?")
    if index >= 0:
        query = request.url[index + 1:]

    since, until, test = -1, -1, ""
    dictionary = cgi.parse_qs(query)
    if "test" in dictionary:
        test = str(dictionary["test"][0])
    if "since" in dictionary:
        since = int(dictionary["since"][0])
    if "until" in dictionary:
        until = int(dictionary["until"][0])

    data_manager.get().query_data(connection, test, since, until)

def api_debug(connection, _):
    """ Implements /api/debug API """
    connection.write(http.writer.compose_error("501", "Not Implemented"))

def api_exit(*_):
    """ Implements /api/exit API """
    raise KeyboardInterrupt

def api_index(connection, _):
    """ Implements /api/index API """
    connection.write(http.writer.compose_error("501", "Not Implemented"))

def api_log(connection, request):
    """ Implements /api/log API """

    query = ""
    index = request.url.find("?")
    if index >= 0:
        query = request.url[index + 1:]

    reverse, verbosity = 0, 0
    dictionary = cgi.parse_qs(query)
    if "reversed" in dictionary:
        reverse = str(dictionary["reversed"][0])
    if "verbosity" in dictionary:
        verbosity = int(dictionary["verbosity"][0])

    log_manager.get().query_logs(connection, reverse, verbosity)

def api_specs(connection, request):
    """ Implements /api/specs API """
    specs_manager.get().query_specs(connection)

def api_runner(connection, request):
    """ Implements /api/runner API """

    query = ""
    index = request.url.find("?")
    if index >= 0:
        query = request.url[index + 1:]

    streaming = 0
    test = ""
    dictionary = cgi.parse_qs(query)
    if "streaming" in dictionary:
        streaming = int(dictionary["streaming"][0])
    if "test" in dictionary:
        test = str(dictionary["test"][0])

    runner.get().run(connection, test, streaming)

def api_state(connection, request):
    """ Implements /api/state API """
    if "?" not in request.url:
        connection.write(state_manager.get().serialize())
    elif request.url.endswith("?t=0"):
        connection.write(state_manager.get().serialize())
    else:
        state_manager.get().comet_wait(connection)

def api_version(connection, _):
    """ Implements /api/version API """
    connection.write(http.writer.compose_response("200", "Ok", {
        "Content-Type": "text/plain",
    }, "0.5.0.0"))

def rootdir(connection, _):
    """ Handler of the / URL """
    state_manager.get().rootdir(connection)