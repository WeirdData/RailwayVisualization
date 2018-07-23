"""
Rohit Suratekar
July 2018

Supporting file to automate extracting geographical information about railway
station code

This script scraps data from website https://indiarailinfo.com

On Windows: Keep 'gecodriver.exe' in the room folder
"""

import time

from numpy import random
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

STATION_DATA_FILE = "stations_data.txt"
# Following file will have columns as (no, state name, acronym)
STATE_NAMES_FILE = "states.csv"

# Following list is needed to clean up station full form
refine_list = ["Double Electric-Line",
               "Single Electric-Line",
               "Single Diesel-Line",
               "Construction - New Line",
               "Quadruple Electric-Line",
               "Construction - Doubling+Electrification",
               "Triple Electric-Line",
               "Construction - Gauge Conversion",
               "Construction - Single-Line Electrification",
               "Narrow Gauge",
               "Construction - Diesel-Line Doubling"]

# Initial setup for selenium
profile = webdriver.FirefoxProfile()

# You might want to change following if you are using proxy
profile.set_preference('network.proxy.Kind', 'Direct')
profile.set_preference('network.proxy.type', 0)

driver = webdriver.Firefox(profile)
driver.get("https://indiarailinfo.com/atlas")


def get_state_names() -> dict:
    """
    Get list of states to convert state names to their acronyms
    Header : No, State Name, Acronym
    :return: Dictionary with keys as full state name and values as acronym
    """
    state_names = {}
    with open(STATE_NAMES_FILE) as f:
        for line in f:
            state_names[line.strip().split(",")[1].strip().lower()] = \
                line.strip(

                ).split(",")[2].strip()

    return state_names


def human_type(element, text) -> None:
    """
    Simulate human typing speed to avoid IP ban
    :param element: Input Element
    :param text: String
    """
    for char in text:
        time.sleep(0.6)  # Average typing speed per second
        element.send_keys(char)


def search(station_name):
    """
    Search Station geographical information from https://indiarailinfo.com
    :param station_name:
    :return:
    """
    name, state, zone = None, None, None
    state_names = get_state_names()

    # Refresh to reload HTML and all of its elements
    driver.refresh()

    try:
        # First get input box
        start_el = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "TrkStnListBox"))
        )

        # Once you get input box, start typing
        human_type(start_el, station_name)
        # Sleep for some random amount so that dropdown items will populate
        time.sleep(random.uniform(0.5, 2))

    except TimeoutException:
        # If could not find input box, return and go to next
        print(station_name + " :Too Slow Skipping")
        return

    try:
        # Get drop down items
        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dropdowntable"))
        )

        count = 1
        station_fount = False
        for m in element.find_elements_by_class_name("rcol"):
            # Select only station which is same as query station
            if m.text == station_name:
                station_fount = True
                break
            else:
                count += 1

        # In station is found, go to that item and click enter
        if station_fount:
            for c in range(count):
                start_el.send_keys(Keys.DOWN)

            start_el.send_keys(Keys.ENTER)

            # Click button to show geographical informTION
            driver.find_element_by_id("SearchTrkStn").click()
            try:

                # Wait till pop-up opens up
                e = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "leaflet-popup-content"))
                )

                # Scrap for state and zone
                for k1 in e.find_elements_by_tag_name("h2"):
                    sp = k1.text.split("/")
                    if sp[0] == station_name:
                        name = sp[1].split("(")[0].strip()
                        for text in refine_list:
                            name = name.replace(text, "")
                        name = name.strip()

                for k2 in e.find_elements_by_tag_name("b"):
                    if k2.text.strip().lower() in state_names.keys():
                        state = state_names[k2.text.strip().lower()]

                    sp = k2.text.split("/")
                    if len(sp) > 1:
                        zone = sp[0]

                # Save it in external file so that even if program is
                # interrupted, you won't lose previously fetched data
                # Remember to open with "a" mode else it will override
                with open(STATION_DATA_FILE, "a") as fn:
                    print(";".join([str(station_name), str(name), str(state),
                                    str(zone)]), file=fn)

            except TimeoutException:
                print(station_name + " :Can not find element")
        else:
            print(station_name + " :No Station Found")
    except TimeoutException:
        print(station_name + " :Exiting")


def download_all(station_names):
    """
    Downloads all the station data and saves it in file
    :param station_names: List of stations
    """
    for k in station_names:
        search(k)
    driver.close()
