import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import random
from random import randint
import sqlite3
random.seed()

def selenium_init():
	chrome_options = Options()
	chrome_options.add_argument("user-data-dir=C:\\Users\\English\\AppData\\Local\\Google\\Chrome\\User Data\\Selenium")
	chrome_options.add_argument('ignore-certificate-errors')
	chrome_options.add_argument('ignore-ssl-errors')
	#chrome_options.add_argument('headless')
	driver = webdriver.Chrome(options=chrome_options)  # Optional argument, if not specified will search path.
	return driver

def pixiv_login(driver, username, password):
	driver.get('https://accounts.pixiv.net/login');
	username = driver.find_element_by_xpath("//input[@type='text'][@autocomplete='username']")
	username.send_keys(username)
	password = driver.find_element_by_xpath("//input[@type='password'][@autocomplete='current-password']")
	password.send_keys(password)
	password.submit()
	time.sleep(3)


def get_work_stats(driver, url, conn):
	driver.get(url)
	time.sleep(15)
	#webElements = driver.find_elements_by_xpath("//a[@class='sc-fzXfPH jPCTIp']")
	webElements = driver.find_elements_by_xpath("//ul//a[starts-with(@href, '/en/artworks/')]")
	#links = driver.find_elements_by_class_name("sc-fzXfPH jPCTIp")
	links = []
	for webElement in webElements:
		links.append(webElement.get_attribute("href"))
	links = list(set(links))
	print(links)
	stats = []
	for link in links:
		driver.get(link)
		wait_val = randint(10,20)
		time.sleep(wait_val)
		#creating data
		access_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S");
		#title = driver.find_element_by_xpath("//h1[@class='sc-LzOkw hoYLUW']").text
		title = driver.find_element_by_xpath("//h1").text
		title = title.replace("'", "''") # escaping single quotes
		likes = driver.find_element_by_xpath("//dd[@title='Like']").text
		bookmarks = driver.find_element_by_xpath("//dd[@title='Bookmarks']").text
		views = driver.find_element_by_xpath("//dd[@title='Views']").text
		likes = likes.replace(',', '')
		bookmarks = bookmarks.replace(',', '')
		views = views.replace(',', '')
		#adding data
		print("adding stats",(access_date,title,likes,bookmarks,views,link))
		stat = (access_date,title,likes,bookmarks,views,link)
		stats.append(stats)
		write_stat_to_db(conn, stat)
		#go back to gallery
		driver.execute_script("window.history.go(-1)")
		back_wait = randint(3,5)
		time.sleep(back_wait)
	return stats

def append_stats(stats):
	with open("stats.txt", "a") as myfile:
		for stat in stats:
			for t in stat:
				myfile.write(str(t))
			myfile.write('\n')

def write_stats_to_db(conn,stats):
	c = conn.cursor()
	for stat in stats:
		# todo: %s could be sql statement: need to sanitize input
		write_stat_to_db(conn,stat)

def write_stat_to_db(conn,stat):
	# todo: %s could be sql statement: need to sanitize input
	c = conn.cursor()
	sql = '''INSERT INTO works VALUES (NULL,'%s','%s','%s','%s','%s','%s')''' %(stat[0],stat[1],stat[2],stat[3],stat[4],stat[5])
	print(sql)
	c.execute(sql)
	conn.commit()

def reset_tables_db(c):
	c.execute('DROP TABLE IF EXISTS works')
	c.execute('''CREATE TABLE works(
		id INTEGER PRIMARY KEY, 
		datetime TEXT, 
		title TEXT, 
		likes INTEGER, 
		bookmarks INTEGER, 
		views INTEGER, 
		link TEXT
		)''')

conn = sqlite3.connect('pixiv_stats.db')
c = conn.cursor()

driver = selenium_init()

urls = []
with open('urls.txt', 'r') as f:
    urls = f.read().split('\n')
    
for url in urls:
	stats = get_work_stats(driver,url,conn)
driver.quit()

conn.commit()
conn.close()




#append_stats([("1","2",datetime.now().strftime("%d/%m/%Y %H:%M:%S"),1)])

