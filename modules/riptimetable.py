#! /usr/bin/env python3
#-*- coding: utf-8 -*-
##
# Cronus module to rip the timetable from SIM connect
# Written by xlanor
##
import time as clock
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from contextlib import closing
from bs4 import BeautifulSoup
import re

class SIMConnect():
	def login(self,username,password,driver):
		url = 'https://simconnect.simge.edu.sg/psp/paprd/EMPLOYEE/HRMS/s/WEBLIB_EOPPB.ISCRIPT1.FieldFormula.Iscript_SM_Redirect?cmd=login'
		
		driver.get(url)
		clock.sleep(5) #we use sleep to let the page happily load throughout the script.
		#finds userinput box
		usr = driver.find_element_by_name('userid')
		#finds password box
		passw = driver.find_element_by_name('pwd')
		#finds login button
		logbtn = driver.find_element_by_name('Submit') 
		usr.send_keys(username)
		passw.send_keys(password)
		logbtn.click()
		clock.sleep(6)
		return driver.page_source

	def navigate_to_latest_timetable(self,driver,latest_term):
		newid = 'SSR_DUMMY_RECV1$sels$'+str(latest_term)+'$$0'
		term_button = driver.find_element_by_id(newid)
		term_button.click()
		continue_button = driver.find_element_by_id('DERIVED_SSS_SCT_SSR_PB_GO')
		continue_button.click()
		clock.sleep(5)#loading the new timetablepage...
		new_formatted_result = driver.page_source
		soup = BeautifulSoup(new_formatted_result,"html.parser")
		return soup

	def type_of_classes(self,row,class_type_dict):
		gettype = row.find("span",{"id":re.compile(r'(MTG_COMP\$)([0-9]{1})')})
		if not gettype.text:
			gettype = row.find("span",{"id":re.compile(r'(MTG_COMP\$)([0-9]{1})([0-9]{1})')})

		if gettype.text.strip():
			type_class = gettype.text
			type_id = int((((gettype.get('id')).split("$"))[1]).strip())
			'''#########################################################
						Only the first row for each type has
							the value of the type.
					ie: row 0, first lecture type will contain 
				lecture., then its blank until row 15, row 15 contains 
				tutorial. We put it into a dict to compare later.
			'''#########################################################
			class_type_dict[type_id] = type_class

	def date_of_classes(self,row):
		getdate = row.find("span",{'id':re.compile(r'(MTG_DATES\$)([0-9]{1})')})
		if not getdate.text.strip():
			getdate = row.find("span",{'id':re.compile(r'(MTG_DATES\$)([0-9]{1})([0-9]{1})')})
		#date is returned in the format DD/MM/YYYY - DD/MM/YYYY
		#because the end date is redundant (unless SIM decides to hold 24hr overnight classes)
		date = getdate.text 
		strippeddate = (((date.strip()).split("-"))[0]).strip() #strips spaces, splits by -, returns first date.

		return strippeddate

	def get_time(self,type,row):
		gettime = row.find("span",{'id':re.compile(r'(MTG_SCHED\$)([0-9]{1})')})
		if not gettime.text.strip():
			gettime = row.find("span",{'id':re.compile(r'(MTG_SCHED\$)([0-9]{1})([0-9]{1})')})
		time = gettime.text
		#time is returned as a value of DD<space>STARTTIME<AM/PM><space>-<space>ENDTIME<AM/PM>
		#removes space, removes DD,splits by -. This forms a list in the format [XXXXAM, YYYYAM] Where x is start, y is end
		strippedtime = (time.strip()[2:]).split("-")
		time = (strippedtime[0]).strip() if type else (strippedtime[1]).strip()
		time = self.format_time(time)
		return time

	def format_time(self,time):
		if len(time) < 7:
			time = "0"+time
		return time

	def get_location(self,row):
		getlocation = row.find("span",{'id':re.compile(r'(MTG_LOC\$)([0-9]{1})')})
		if not getlocation.text.strip():
			getlocation = row.find("span",{'id':re.compile(r'(MTG_LOC\$)([0-9]{1})([0-9]{1})')})

		return getlocation.text

	def get_row_id(self,row):
		getlocation = row.find("span",{'id':re.compile(r'(MTG_LOC\$)([0-9]{1})')})
		if not getlocation.text.strip():
			getlocation = row.find("span",{'id':re.compile(r'(MTG_LOC\$)([0-9]{1})([0-9]{1})')})

		rowid = (((getlocation.get('id')).split("$"))[1]).strip()
		return rowid

	def determine_class_type(self,list_of_class_type_keys,class_type_dict,no_of_keys,rowid):
		counter = 0
		trigger = True
		while trigger :
			actual_class_type = ""
			if int(rowid) >= int(list_of_class_type_keys[counter]):
				actual_class_type = class_type_dict[list_of_class_type_keys[counter]]
				counter += 1
				if counter >= (no_of_keys):
					trigger = False			
			else:
				trigger = False

		return actual_class_type

	def handle_single_digit_row(self,singledigittablerow,class_type_dict,list_of_results,subjectitlename):
		for row in singledigittablerow:
			'''####################################################################################
									Here we're going to use regex.
							Why do we repeat same regex twice with variance?
							First we check for id with regex for single digit
									For example, MTG_DATES$0
					If in that div, MTGDATES$# WHERE # is a random number does not match regex, 
						It means that we're in a row where MTGDATES$ is MTGDATES$##
								Thus we write another regex for that row.
				This was probably never meant to be pulled as an API that's why its so fucked up.
			'''####################################################################################
			self.type_of_classes(row,class_type_dict)
			strippeddate = self.date_of_classes(row)
			
			starttime = strippeddate +" "+ self.get_time(True,row)
			endtime = strippeddate +" "+ self.get_time(False,row)

			location = self.get_location(row)

			# Time to determine class type (lecture, tutorial) from the array above.
			rowid = self.get_row_id(row)
			
			list_of_class_type_keys = list(class_type_dict.keys())
			list_of_class_type_keys = sorted(list_of_class_type_keys)
			no_of_keys = len(list_of_class_type_keys)
			actual_class_type = self.determine_class_type(list_of_class_type_keys,class_type_dict,no_of_keys,rowid)
			
			resultdict = {"class_name":subjectitlename,"date":strippeddate,"Start_Time":starttime,"End_Time":endtime,"Location":location,"Type":actual_class_type}
			list_of_results.append(resultdict)

	def process_subject_div(self,subjectdiv,class_type_dict,list_of_results):
		for div in subjectdiv:
			class_type_dict.clear()
			subjectitle = div.find("td",{'class':'PAGROUPDIVIDER'})
			subjectitlename = subjectitle.text
			singledigittablerow = div.findAll('tr',{'id':re.compile(r'(trCLASS_MTG_VW\$)([0-9]{1})(_row)([0-9]{1})')})
			self.handle_single_digit_row(singledigittablerow,class_type_dict,list_of_results,subjectitlename)
			
	def timetable(self,username,password):
		#"API" that populates timetable. It was never designed for this purpose, but we're going to use it
		url3 = 'https://simconnect1.simge.edu.sg:444/psc/csprd_2/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSR_SSENRL_LIST.GBL'
		#initialize PhantomJS, define settings
		driver = webdriver.PhantomJS(executable_path='./phantomjs',service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
		driver.set_window_size(1124, 850) 
		page_source = self.login(username,password,driver)
		if 'https://simconnect.simge.edu.sg/psp/paprd/EMPLOYEE/EMPL/?cmd=logout' in page_source:
			driver.get(url3) 
			formatted_result = driver.page_source
			soup = BeautifulSoup(formatted_result,"html.parser")
			termdiv = soup.findAll('span',{'id':re.compile(r'(TERM_CAR\$)([0-9]{1})')})
			if len(termdiv) != 0:
				latest_term = len(termdiv)-1
				soup = self.navigate_to_latest_timetable(driver,latest_term)
			
			subjectdiv = soup.findAll('div',{'id':re.compile(r'(win2divDERIVED_REGFRM1_DESCR20\$)([0-9]{1})')})
			class_type_dict = {}
			list_of_results = []
			self.process_subject_div(subjectdiv,class_type_dict,list_of_results)
			return(list_of_results)
			driver.close()
		else:
			driver.close()
			return []

