from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

MATHSCINET_AUTHOR_SEARCH_URL = "https://mathscinet-ams-org.proxy2.library.illinois.edu/mathscinet/searchauthors.html"

# the two lines below are from here:
# https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/#1-driver-management-software
service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 60)

with open("names.txt", "r") as f:
    names = f.read().splitlines()[:3]

df = []

for name in names:
    driver.get(MATHSCINET_AUTHOR_SEARCH_URL)

    # wait up to 60 seconds for the user to log in
    author_name_input_field = wait.until(EC.visibility_of_element_located((By.NAME, "authorName")))

    author_name_input_field.send_keys(name)
    author_name_input_field.send_keys(Keys.ENTER)

    if driver.find_elements(By.CLASS_NAME, "matches"):
        # there were no matches or multiple matches for the name, so we're still on the search results page
        # instead of the profile page of a specific author
        # just append the name and leave the rest of the columns blank
        df.append([name])
        continue

    table_cells = driver.find_elements(By.TAG_NAME, "td")
    total_citations = None
    total_publications = None

    for prev_cell, curr_cell in zip(table_cells[:-1], table_cells[1:]):
        if prev_cell.text == "Total Publications:":
            total_publications = wait.until(lambda driver: curr_cell.text)
        elif prev_cell.text == "Total Citations:":
            total_citations = wait.until(lambda driver: curr_cell.text)
            # need to wait a bit for the text to show up in the table cells
            # mathscinet probably needs some time to get the data from a database

    df.append([name, int(total_publications), int(total_citations)])

df = pd.DataFrame(df, columns=["Name", "Total Publications", "Total Citations"])
df.set_index("Name", inplace=True)
df.loc["Total"] = df.sum()

df.to_csv("output.csv")
