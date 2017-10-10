#! /usr/bin/env python3
#-*- coding: utf-8 -*-
##
# Cronus test_login 
# Written by xlanor
##
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from contextlib import closing
from bs4 import BeautifulSoup
import re


class loginTest():
	def testlogin (self,username,password):
		url = 'https://simconnect.simge.edu.sg/psp/paprd/EMPLOYEE/HRMS/s/WEBLIB_EOPPB.ISCRIPT1.FieldFormula.Iscript_SM_Redirect?cmd=login'
		driver = webdriver.PhantomJS(executable_path='./phantomjs',service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
		driver.set_window_size(1124, 850)  
		driver.get(url)
		time.sleep(5) #we use sleep to let the page happily load throughout the script. 
		usr = driver.find_element_by_name('userid')
		#finds password box
		passw = driver.find_element_by_name('pwd')
		#finds login button
		logbtn = driver.find_element_by_name('Submit')
		#login
		usr.send_keys(username)
		passw.send_keys(password)
		logbtn.click()
		time.sleep(6)
		if 'https://simconnect.simge.edu.sg/psp/paprd/EMPLOYEE/EMPL/?cmd=logout' in driver.page_source:
			driver.close()
			return "true"
		else:
			driver.close()
			return "false"