import time

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def search_file(string: str, driver: object):
	time.sleep(0.2)
	links = driver.find_elements(By.TAG_NAME, "a")
	for link in links:
		href = link.get_attribute("href")
		if href is not None and href.find(string) != -1:
			print(href)
			#driver.get(href)
			# time.sleep(1)
			#driver.back()
			#time.sleep(1)


def parsing(driver):
	time.sleep(0.2)
	search_box = driver.find_elements(By.CLASS_NAME, "wLL07_0Xnd1QZpzpfR4W")
	for i in range(len(search_box)):
		search_box[i].click()
		search_file(string=".dll", driver=driver)
		driver.back()


def entry_point(name_lib: str):
	driver: object = webdriver.Chrome()
	driver.get("https://duckduckgo.com/")

	search_box: object = driver.find_element(By.ID, "search_form_input_homepage")
	search_box.send_keys(name_lib)
	search_box.send_keys(Keys.ENTER)

	parsing(driver)
	driver.quit()
