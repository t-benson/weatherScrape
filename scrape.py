# Scrape weather from:
# https://www.almanac.com/weather/history/MA/Boston/1984-01-14

import mysql.connector
import time
from datetime import date
from datetime import timedelta
import pprint
import time
import re
import urllib
from urllib import request


def get_temps(date, city="Boston", state="MA"):  # example: (1982-01-01, Boston, MA)

    min_reg = r'Minimum Temperature</h3></th><td><p><span class="value">(.+?)</span>'
    max_reg = r'Maximum Temperature</h3></th><td><p><span class="value">(.+?)</span>'
    mean_reg = r'Mean Temperature</h3></th><td><p><span class="value">(.+?)</span>'

    url = 'https://www.almanac.com/weather/history/' + state + '/' + city + '/' + date
    hdr = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)' }

    req = urllib.request.Request(url, headers=hdr)
    response = urllib.request.urlopen(req)

    #response_info = response.info()

    #response_code = response.code
    #response_reason = response.reason
    #response_headers = response.headers
    
    #print(response_code)
    #print(response_reason)
    #print(response_headers)

    html_page = response.readlines()
    html_page = str(html_page)

    min_match = re.search(min_reg, html_page)
    max_match = re.search(max_reg, html_page)
    mean_match = re.search(mean_reg, html_page)

    guid = date + '_' + city + '_' + state

    return (guid, date, city, state, min_match.group(1), max_match.group(1), mean_match.group(1))


def update_db(_date, city="Boston", state="MA"):
    
    cnx = mysql.connector.connect(user='scrape', password='P@ssw0rd123^',
                              host='192.168.0.25', database='temperatures')
    
    cursor = cnx.cursor()

    add_scrape = ("INSERT INTO scrapes "
               "(first_name, last_name, hire_date, gender, birth_date) "
               "VALUES (%s, %s, %s, %s, %s)")

    db_values = get_temps(_date, city, state)

    print(db_values)

    s_year = int(db_values[1][0:4])
    s_month = int(db_values[1][5:7])
    s_day = int(db_values[1][8:11])

    print(s_year)
    print(s_month)
    print(s_day)

    print(type(s_year))
    print(type(s_month))
    print(type(s_day))

    scrape_date = date(s_year, s_month, s_day)

    print(scrape_date)
    
    data_scrape = {
      'guid': db_values[0],
      'date': scrape_date,
      'city': db_values[2],
      'state': db_values[3],
      'low': float(db_values[4]),
      'high': float(db_values[5]),
      'mean': float(db_values[6])
    }

    add_scrape = ("INSERT INTO scrapes "
                  "(guid, date, city, state, low, high, mean) "
                  "VALUES (%(guid)s, %(date)s, %(city)s, %(state)s, %(low)s, %(high)s, %(mean)s)")

    cursor.execute(add_scrape, data_scrape)

    cnx.commit()

    cursor.close()

    cnx.close()


def scrape_dates(beg_date, end_date):  # ('1982-01-01', '1983-01-31')

    beg_date = date( int(beg_date[0:4]), int(beg_date[5:7]), int(beg_date[8:10]) )
    end_date = date( int(end_date[0:4]), int(end_date[5:7]), int(end_date[8:10]) )

    #if end_date - beg_date < timedelta(0): return
    
    _scrape_dates = []

    for i in range(((end_date - beg_date).days) + 1):
        _scrape_dates.append( str(beg_date + timedelta(i)) )

    _scrape_data = []

    for _date in _scrape_dates:
        _temp = get_temps(_date)
        _scrape_data.append((_temp))
        time.sleep(0)

    return _scrape_data


def compare_date(date1, date2, city="Boston", state="MA"):
    temp1 = get_temps(date1, city, state)
    temp2 = get_temps(date2, city, state)
    
    print(temp1)
    print(temp2)

    if temp1[4] == temp2[4]: print("Avg temp was the same on", temp1[0], "and", temp2[0])
    elif temp1[4] > temp2[4]: print("It was", float(temp1[4]) - float(temp2[4]), "degrees hotter on average on", temp1[0], "than", temp2[0])
    elif temp1[4] < temp2[4]: print("It was", float(temp2[4]) - float(temp1[4]), "degrees hotter on average on", temp2[0], "than", temp1[0])
    else: return None


# testing

# get_temps("1982-01-02", "Boston", "MA")

# compare_date("1984-01-01", "2017-01-01")
