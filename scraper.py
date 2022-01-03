from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

FACULTY_LIST_URL = "https://math.illinois.edu/directory/faculty"

# selector for all divs which directly contain the name of a faculty member
CSS_SELECTOR = ".field-name-field-dircore-display-name .field__item"

MATHSCINET_AUTHOR_SEARCH_URL = "https://mathscinet-ams-org.proxy2.library.illinois.edu/mathscinet/searchauthors.html"

# the two lines below are from here:
# https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/#1-driver-management-software
service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 60)

driver.get(FACULTY_LIST_URL)

divs_containing_names = driver.find_elements(By.CSS_SELECTOR, CSS_SELECTOR)
names = [div.text for div in divs_containing_names]
print(names)

with open("output.txt", "w") as outfile:
    for name in names:
        driver.get(MATHSCINET_AUTHOR_SEARCH_URL)

        # wait up to 60 seconds for the user to log in
        author_name_input_field = wait.until(EC.visibility_of_element_located((By.NAME, "authorName")))

        author_name_input_field.send_keys(name)
        author_name_input_field.send_keys(Keys.ENTER)

        print("==================================", file=outfile)
        print(name, file=outfile)

        match_divs = driver.find_elements(By.CLASS_NAME, "matches")
        if match_divs:
            # there were no matches or multiple matches for the name, so we're still on the search results page
            # instead of the profile page of a specific author
            if match_divs[0].text == "Matches: 0":
                print("No matches were found for this name on MathSciNet", file=outfile)
            else:
                # TODO: is there a way to get university affiliation from MathSciNet to filter out some matches?
                print("Multiple matches were found for this name on MathSciNet", file=outfile)
            continue

        table_cells = driver.find_elements(By.TAG_NAME, "td")
        total_citations = None
        total_publications = None

        # TODO: analyze table cells by <tr> (table rows) instead?
        for prev_cell, curr_cell in zip(table_cells[:-1], table_cells[1:]):
            if prev_cell.text == "Total Publications:":
                total_publications = wait.until(lambda driver: curr_cell.text)
            elif prev_cell.text == "Total Citations:":
                total_citations = wait.until(lambda driver: curr_cell.text)
                # need to wait a bit for the text to show up in the table cells
                # mathscinet probably needs some time to get the data from a database

        print("Total Publications:", total_publications, file=outfile)
        print("Total Citations:", total_citations, file=outfile)
