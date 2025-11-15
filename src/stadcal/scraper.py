from datetime import datetime
from zoneinfo import ZoneInfo
import logging

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)
tz = ZoneInfo("Europe/Stockholm")

class ServiceInfo:
    def __init__(self, summary, start, end):
        self.summary = summary
        self.start = start
        self.end = end

    def __str__(self):
        return f"<ServiceInfo,{self.summary}, {self.start}, {self.end}>"

    def __repr__(self):
        return str(self)


    @staticmethod
    def from_service_info_str(service_info_str):
        #return [s.text_content().replace("\t", "").strip().split("\n \n") for s in service_infos]
        si_li = service_info_str.replace("\t", "").strip().split("\n \n")
        return ServiceInfo(si_li[0],
                           ServiceInfo.get_start_time(si_li),
                           ServiceInfo.get_end_time(si_li))

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

def _get_service_infos(username, password):
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

        # go to services
        page.wait_for_selector("xpath=//a[@href='/services']")
        services_button = page.locator("xpath=//a[@href='/services']")
        services_button.click()

        #page.wait_for_selector(".service-info")
        page.wait_for_selector("xpath=//div[@class='customer-mission upcoming']")
        service_infos = page.locator("xpath=//div[@class='customer-mission upcoming']/div/div[@class='service-info']").all()
        service_info_strs = [si.text_content() for si in service_infos]

        return service_info_strs

def get_events_from_source(username, password):
    service_info_strs = _get_service_infos(username, password)
    return [ServiceInfo.from_service_info_str(si) for si in service_info_strs]
