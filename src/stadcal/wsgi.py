from flask import Flask, make_response
from . import cal
from apscheduler.schedulers.background import BackgroundScheduler
import tomllib
from . import scraper
import os
import logging
import sys
logger = logging.getLogger(__name__)

os.environ["SELENIUM_BROWSER_CACHE_DIR"] = "/tmp/selenium"
os.environ["SE_CACHE_PATH"] = "/tmp/selenium"

def create_app(config_path):
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    app = Flask(__name__)
    scheduler = BackgroundScheduler()
    logger.info("Create app")
    logger.info(f"Creating app: config_path={config_path}")
    if app.config.from_file(config_path, load=tomllib.load, text=False):
        logger.info("successfully loaded config")

    def renew_calendar():
        logger.info("renew calendar")
        serviceInfos = scraper.get_events_from_source(app.config["USERNAME"], app.config["PASSWORD"])
        calendar = cal.from_service_info(serviceInfos)
        app.config["calendar"] = calendar
        logger.info("renew calendar done")
    renew_calendar()

    @app.route("/")
    def hello_world():
        logger.info("Request hello world")
        return "<p>hello world</p>"

    @app.route("/stadalliansen.ics")
    def ics():
        logger.info("Request ics")
        logger.info(app.config["calendar"])

        response = make_response(app.config["calendar"].to_ical().decode("ascii"), 200)
        response.mimetype = "text/calendar"
        return response

    #scheduler.add_job(renew_calendar) # Run once immediately
    scheduler.add_job(renew_calendar, "interval", minutes=60)
    scheduler.start()
    return app
