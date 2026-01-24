from datetime import datetime
from zoneinfo import ZoneInfo
import logging

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)
tz = ZoneInfo("Europe/Stockholm")

class Mission:
    def __init__(self, name, start, end, employee_names):
        self.name = name
        self.start = start
        self.end = end
        self.employee_names = employee_names

    def __str__(self):
        return f"<Mission,{self.name}, {self.start}, {self.end} {self.employee_names}>"

    def __repr__(self):
        return str(self)

    @staticmethod
    def get_start_time(service_info_li):
        start_time_str = service_info_li[2].split(" ")[-3]
        dt_start = datetime.strptime(service_info_li[1] + " " + start_time_str, "%d %b %Y %H:%M")
        dt_start = dt_start.replace(tzinfo=tz)
        return dt_start

    @staticmethod
    def get_end_time(service_info_li):
        end_time_str = service_info_li[2].split(" ")[-1]
        dt_end = datetime.strptime(service_info_li[1] + " " + end_time_str, "%d %b %Y %H:%M")
        dt_end = dt_end.replace(tzinfo=tz)
        return dt_end

    @staticmethod
    def from_service_locator(locator):
        name = locator.locator("xpath=//div[@class='service-name']").text_content().strip()
        date = locator.locator("xpath=//div[@class='service-date']").text_content().strip()
        scheduled_time = locator.locator("xpath=//div[@class='scheduled-time']/span").text_content().strip()
        start_time = scheduled_time.split(" - ")[0]
        end_time = scheduled_time.split(" - ")[1]
        dt_start = datetime.strptime(f"{date} {start_time}", "%d %b %Y %H:%M")
        dt_end = datetime.strptime(f"{date} {end_time}", "%d %b %Y %H:%M")
        employee_names = [l.text_content() for l in locator.locator("xpath=//div[@class='employee-name']").all()]
        return Mission(name, dt_start, dt_end, employee_names)

    @staticmethod
    def from_home_locator(locator):
        name = locator.locator("xpath=//div[@class='service']").text_content()
        date = locator.locator("xpath=//div[@class='the-date']").text_content().strip()
        scheduled_time = locator.locator("xpath=//div[@class='the-time']").text_content().strip()
        start_time = scheduled_time.split(" - ")[0]
        end_time = scheduled_time.split(" - ")[1]
        dt_start = datetime.strptime(f"{date} {start_time}", "%d %b %Y %H:%M")
        dt_end = datetime.strptime(f"{date} {end_time}", "%d %b %Y %H:%M")
        return Mission(name, dt_start, dt_end, ["unassigned"])


def get_missions_from_stadalliansen(username, password):
    """Returns a list of missions, missions have the required info for a calendar event"""
    with sync_playwright() as p:
        browser=p.firefox.launch(headless=True)
        page=browser.new_page()

        # Login
        page.goto("https://stadalliansen.städportalen.se/")
        username_box=page.locator("xpath=//input[starts-with(@placeholder, 'Användarnamn')]")
        password_box = page.locator("xpath=//input[starts-with(@type, 'password')]")
        submit_button = page.get_by_role("button")
        username_box.fill(username)
        password_box.fill(password)
        submit_button.click()

        # go to services page
        page.wait_for_selector("xpath=//a[@href='/services']")
        services_button = page.locator("xpath=//a[@href='/services']")
        services_button.click()
        page.wait_for_selector("xpath=//div[@class='missions']")

        # get all missions from service page
        service_mission_locators = page.locator("xpath=//div[@class='missions']/span/div").all()

        for m in service_mission_locators:
            m.locator("xpath=//i[@class='fas fa-chevron-down']").click() # the click action results in fetching employee details
        service_missions = [Mission.from_service_locator(m) for m in service_mission_locators]

        # go to home to get next unassigned future event
        home_button = page.locator("xpath=//a[@href='/customer-home']")
        home_button.click()
        page.wait_for_selector("xpath=//div[@class='c-box next']")

        # Get the mission from home page
        home_mission_locator = page.locator("xpath=//div[@class='c-box next']")
        home_mission = Mission.from_home_locator(home_mission_locator)

        return service_missions + [home_mission]
