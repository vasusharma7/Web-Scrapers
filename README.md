# Web-Scrapers

Web Scrapers written in python using Selenium and BeautifulSoup

Once run the scrapers will extract all the reviews from Trip Advisor/ Yelp of a particular Hotel ( Hotel URL to be changed in the script).
All the reviews along with associated user information such as username, profile photo, review date, respose etc  will be stored in the local MongoDB database.

The reviews will be extracted right from the time they were first posted. So it will take time on fisrt run as the number of reviews may sometimes go beyond 250 pages also.
If run again, the scrapers will only extract the new reviews.

## Requirements
```bash
Python 3.6+
Selenium
BeautifulSoup
PyMongo
ChromeDriver compatible to your chrome version
```
