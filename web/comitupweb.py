#!/usr/bin/python3
# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE

#
# Copyright 2016-2017 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

import logging
import sys
import time
import urllib
from logging.handlers import TimedRotatingFileHandler
from multiprocessing import Process

from cachetools import TTLCache, cached
from flask import (
    Flask,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
)

sys.path.append(".")
sys.path.append("..")

from comitup import client as ciu  # noqa

ciu_client = None  # type: ignore
LOG_PATH = "/var/log/comitup-web.log"
TEMPLATE_PATH = "/usr/share/comitup/web/templates"

ttl_cache: TTLCache = TTLCache(maxsize=10, ttl=5)


def deflog():
    log = logging.getLogger("comitup_web")
    log.setLevel(logging.INFO)
    handler = TimedRotatingFileHandler(
        LOG_PATH,
        encoding="utf=8",
        when="W0",
        backupCount=8,
    )
    fmtr = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(fmtr)
    log.addHandler(handler)

    return log


def do_connect(ssid, password, log):
    time.sleep(1)
    log.debug("Calling client connect")
    ciu_client.service = None  # type: ignore
    ciu_client.ciu_connect(ssid, password)  # type: ignore


def get_zt_id():
    with open("/var/lib/zerotier-one/identity.public") as f:
        return f.readline().split(":")[0]


def get_cpu_id():
    with open("/proc/cpuinfo") as f:
        for line in f:
            if line.startswith("Serial"):
                return line.split(":")[1].strip()
    return "unknown"


@cached(cache=ttl_cache)
def cached_points():
    return ciu_client.ciu_points()  # type: ignore


def create_app(log):
    app = Flask(__name__, template_folder=TEMPLATE_PATH)

    @app.after_request
    def add_header(response):
        response.cache_control.max_age = 0
        return response

    @app.route("/")
    def index():
        points = cached_points()
        for point in points:
            point["ssid_encoded"] = urllib.parse.quote(  # type: ignore
                point["ssid"]
            )
        log.info("index.html - {} points".format(len(points)))
        # get zt_id with `cat /var/lib/zerotier-one/identity.public | cut -d ':' -f1`
        # get cpu_id with `cat /proc/cpuinfo | grep Serial | awk '{print $3}'`
        zt_id = get_zt_id()
        cpu_id = get_cpu_id()
        return render_template(
            "index.html",
            points=points,
            can_blink=ciu.can_blink(),
            zt_id=zt_id,
            cpu_id=cpu_id,
        )

    @app.route("/confirm")
    def confirm():
        ssid = request.args.get("ssid", "")
        ssid_encoded = urllib.parse.quote(ssid.encode())  # type: ignore
        encrypted = request.args.get("encrypted", "unencrypted")

        mode = ciu_client.ciu_info()["imode"]  # type: ignore

        log.info("confirm.html - ssid {0}, mode {1}".format(ssid, mode))

        return render_template(
            "confirm.html",
            ssid=ssid,
            encrypted=encrypted,
            ssid_encoded=ssid_encoded,
            mode=mode,
            can_blink=ciu.can_blink(),
        )

    @app.route("/connect", methods=["POST"])
    def connect():
        ssid = urllib.parse.unquote(request.form["ssid"])  # type: ignore
        password = request.form["password"].encode()

        cached_points()

        p = Process(target=do_connect, args=(ssid, password, log))
        p.start()

        log.info("connect.html - ssid {0}".format(ssid))
        return render_template(
            "connect.html",
            ssid=ssid,
            password=password,
        )

    @app.route("/blink")
    def blink():
        log.info("blinking")
        ciu.blink()

        resp = jsonify(success=True)
        return resp

    @app.route("/img/favicon.ico")
    def favicon():
        log.info("Returning 404 for favicon request")
        abort(404)

    @app.route("/img/<path:path>")
    def send_image(path):
        return send_from_directory(TEMPLATE_PATH + "/images", path)

    @app.route("/js/<path:path>")
    def send_js(path):
        return send_from_directory(TEMPLATE_PATH + "/js", path)

    @app.route("/css/<path:path>")
    def send_css(path):
        return send_from_directory(TEMPLATE_PATH + "/css", path)

    @app.route("/<path:path>")
    def catch_all(path):
        log.info("Redirecting {0}".format(path))
        return redirect("http://10.41.0.1/", code=302)

    @app.errorhandler(500)
    def internal_error(error):
        log.error("Internal Error detected")
        sys.exit(1)

    return app


def main():
    log = deflog()
    log.info("Starting comitup-web")

    global ciu_client
    ciu_client = ciu.CiuClient()

    ciu_client.ciu_state()
    ciu_client.ciu_points()

    app = create_app(log)
    app.run(host="0.0.0.0", port=80, debug=False, threaded=True)


if __name__ == "__main__":
    main()
