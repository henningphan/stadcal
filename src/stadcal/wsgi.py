from flask import Flask, make_response
from . import cal
from apscheduler.schedulers.background import BackgroundScheduler
import tomllib
from . import scraper

def create_app(config_path):
    app = Flask(__name__)
    scheduler = BackgroundScheduler()
    print(f"Creating app: config_path={config_path}")
    if app.config.from_file(config_path, load=tomllib.load, text=False):
        print("successfully loaded config")

    def renew_calendar():
        print("echo hi")

    @app.route("/")
    def hello_world():
        return "<p>hello world</p>"

    @app.route("/stadalliansen.ics")
    def ics():
        serviceInfos = scraper.get_events_from_source(app.config["USERNAME"], app.config["PASSWORD"])
        calendar = cal.from_service_info(serviceInfos)

        response = make_response(calendar.to_ical().decode("ascii"), 200)
        response.mimetype = "text/calendar"
        return response

    scheduler.add_job(renew_calendar) # Run once immediately
    scheduler.add_job(renew_calendar, "interval", minutes=1)
    scheduler.start()
    return app
