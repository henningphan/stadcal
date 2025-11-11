from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from datetime import datetime
import time
from zoneinfo import ZoneInfo

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
        si_li = service_info_str.split("\n")
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
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get("https://stadalliansen.städportalen.se/")

    title = driver.title

    driver.implicitly_wait(0.5)

    username_box = driver.find_element(by=By.XPATH, value="//input[starts-with(@placeholder, 'Användarnamn')]")
    submit_button = driver.find_element(by=By.TAG_NAME, value="button")

    password_box = driver.find_element(by=By.XPATH, value="//input[starts-with(@type, 'password')]")
    username_box.send_keys(username)
    password_box.send_keys(password)
    submit_button.click()
    time.sleep(1)
    services_button = driver.find_element(by=By.XPATH, value="//a[@href='/services']")
    services_button.click()

    timeout_s = 20
    wait = WebDriverWait(driver, timeout_s)# .until(EC.element_to_be_clickable((By.TAG_NAME, "button"))).click()
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "service-info")))

    service_infos_str = [e.text for e in driver.find_elements(by=By.CLASS_NAME, value="service-info")]
    driver.quit()
    return service_infos_str

def get_events_from_source(username, password):
    service_infos = _get_service_infos(username, password)
    return [ServiceInfo.from_service_info_str(si) for si in service_infos]
