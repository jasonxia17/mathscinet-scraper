# mathscinet-scraper

### Setup and Running the Code
Clone this repository and `cd` into the repository folder. Then, run the following commands:
```
pip install selenium webdriver_manager pandas
python3 scraper.py
```

### Input and Output
The input (a list of names) is provided in `names.txt`. The publication and citation statistics are `output.csv`. If the database found no matches or multiple matches for a name, the statistics in that row will not be filled in.

### Notes
You need to manually log in when the Shibboleth page appears. If you don't log in within 60 seconds, the script will time out and crash.
