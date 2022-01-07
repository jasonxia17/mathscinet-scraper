from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

MATHSCINET_AUTHOR_SEARCH_URL = "https://mathscinet-ams-org.proxy2.library.illinois.edu/mathscinet/searchauthors.html"
MATHSCINET_PUBLICATIONS_SEARCH_URL = "https://mathscinet-ams-org.proxy2.library.illinois.edu/mathscinet/search.html"

START_YEAR = 2018
END_YEAR = 2022

# the two lines below are from here:
# https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/#1-driver-management-software
service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 60)

with open("names.txt", "r") as f:
    names = f.read().splitlines()

df = []

for name in names:
    print(name)
    driver.get(MATHSCINET_AUTHOR_SEARCH_URL)

    # wait up to 60 seconds for the user to log in
    author_name_input_field = wait.until(EC.visibility_of_element_located((By.NAME, "authorName")))

    author_name_input_field.send_keys(name)
    author_name_input_field.send_keys(Keys.ENTER)

    if driver.find_elements(By.CLASS_NAME, "matches"):
        # There were no matches or multiple matches for the name, so we're still on the search results page
        # instead of the profile page of a specific author.
        # In this situation, we'll just append the name and leave the rest of the columns blank.
        df.append([name])
        continue

    table_cells = driver.find_elements(By.TAG_NAME, "td")
    total_citations = 0
    total_publications = 0

    for prev_cell, curr_cell in zip(table_cells[:-1], table_cells[1:]):
        if prev_cell.text == "Total Publications:":
            total_publications = wait.until(lambda driver: curr_cell.text)
        elif prev_cell.text == "Total Citations:":
            total_citations = wait.until(lambda driver: curr_cell.text)
            # need to wait a bit for the text to show up in the table cells
            # mathscinet probably needs some time to get the data from a database

    # name as stored in the database; need this when searching for publications
    official_name = driver.find_element(By.CLASS_NAME, "authorName").text

    driver.get(MATHSCINET_PUBLICATIONS_SEARCH_URL)
    author_name_input_field = wait.until(EC.visibility_of_element_located((By.NAME, "s4")))
    author_name_input_field.send_keys(official_name)
    driver.find_element(By.ID, "yearrange").click()
    driver.find_element(By.ID, "yearRangeFirst").send_keys(START_YEAR)
    driver.find_element(By.ID, "yearRangeSecond").send_keys(END_YEAR)
    author_name_input_field.send_keys(Keys.ENTER)

    try:
        # If there are multiple pages, click "Show all results" to display them all on a single page
        driver.find_element(By.CSS_SELECTOR, ".extendHeadlines a").click()
    except NoSuchElementException:
        # Results already fit on a single page, we don't need to do anything
        pass

    try:
        # Only one publication matches, so we're on a publication page instead of search results page
        citations_in_date_range = driver.find_element(By.CSS_SELECTOR, ".citationCounts p").text.split(": ")[1]
        publications_in_date_range = 1

    except NoSuchElementException:
        try:
            publications_in_date_range = driver.find_element(By.CLASS_NAME, 'matches').text.split()[1]
        except NoSuchElementException:
            publications_in_date_range = 0

        citations_in_date_range = 0

        while True:
            for a in driver.find_elements(By.CSS_SELECTOR, '.headlineMenu a'):
                if "Citation" in a.text:
                    citations_in_date_range += int(a.text.split()[0])

            nav_links = driver.find_elements(By.CSS_SELECTOR, '.navbar a')
            if not nav_links or nav_links[-1].text != "Next":
                break

            # Keep clicking "Next" while it is clickable
            # Still need to do this because when there are >100 results, "Show all results" is not
            # an option; it can only display 100 results at a time.
            nav_links[-1].click()

    df.append([name, int(total_publications), int(total_citations),
               int(publications_in_date_range), int(citations_in_date_range)])

df = pd.DataFrame(df, columns=["Name", "Total Publications", "Total Citations",
                              "Publications in Date Range", "Citations in Date Range"])

df.set_index("Name", inplace=True)
df.loc["Total"] = df.sum()

df.to_csv("output.csv")
