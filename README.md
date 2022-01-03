# mathscinet-scraper

### Setup and Running the Code
Clone this repository and `cd` into the repository folder. Then, run the following commands:
```
pip install selenium
pip install webdriver_manager
python3 scraper.py
```

### Example Output
See `output.txt` for an example output when this script is run on the UIUC math department's faculty list.

### Notes
To use this script on a different department/school's faculty list, you need to change `FACULTY_LIST_URL` to the appropriate website, and you need to change `CSS_SELECTOR` based on the structure of that website's HTML. It might take a bit of trial and error to find a selector that works properly.
