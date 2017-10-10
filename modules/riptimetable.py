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
	def timetable(self,username,password):
		url = 'https://simconnect.simge.edu.sg/psp/paprd/EMPLOYEE/HRMS/s/WEBLIB_EOPPB.ISCRIPT1.FieldFormula.Iscript_SM_Redirect?cmd=login'
		#"API" that populates timetable. It was never designed for this purpose, but we're going to use it
		url3= 'https://simconnect1.simge.edu.sg:444/psc/csprd_2/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSR_SSENRL_LIST.GBL' 
		#initialize PhantomJS, define settings
		driver = webdriver.PhantomJS(executable_path='./phantomjs',service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
		driver.set_window_size(1124, 850)  
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
		if 'https://simconnect.simge.edu.sg/psp/paprd/EMPLOYEE/EMPL/?cmd=logout' in driver.page_source:
			driver.get(url3) 
			formatted_result = driver.page_source
			soup = BeautifulSoup(formatted_result,"html.parser")
			subjectdiv = soup.findAll('div',{'id':re.compile(r'(win2divDERIVED_REGFRM1_DESCR20\$)([0-9]{1})')})
			class_type_dict = {}
			list_of_results = []

			for div in subjectdiv:
				class_type_dict.clear()
				subjectitle = div.find("td",{'class':'PAGROUPDIVIDER'})
				subjectitlename = subjectitle.text
				singledigittablerow = div.findAll('tr',{'id':re.compile(r'(trCLASS_MTG_VW\$)([0-9]{1})(_row)([0-9]{1})')})

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
					gettype = row.find("span",{"id":re.compile(r'(MTG_COMP\$)([0-9]{1})')})
					if not gettype.text:
						gettype = row.find("span",{"id":re.compile(r'(MTG_COMP\$)([0-9]{1})([0-9]{1})')})
					if gettype.text.strip():
						type_class = gettype.text
						type_id = int((((gettype.get('id')).split("$"))[1]).strip())
						class_type_dict[type_id] = type_class
					getdate = row.find("span",{'id':re.compile(r'(MTG_DATES\$)([0-9]{1})')})
					if not getdate.text.strip():
						getdate = row.find("span",{'id':re.compile(r'(MTG_DATES\$)([0-9]{1})([0-9]{1})')})
					#date is returned in the format DD/MM/YYYY - DD/MM/YYYY
					#because the end date is redundant (unless SIM decides to hold 24hr overnight classes)
					date = getdate.text 
					strippeddate = (((date.strip()).split("-"))[0]).strip() #strips spaces, splits by -, returns first date.
					gettime = row.find("span",{'id':re.compile(r'(MTG_SCHED\$)([0-9]{1})')})
					if not gettime.text.strip():
						gettime = row.find("span",{'id':re.compile(r'(MTG_SCHED\$)([0-9]{1})([0-9]{1})')})
					time = gettime.text
					#time is returned as a value of DD<space>STARTTIME<AM/PM><space>-<space>ENDTIME<AM/PM>
					strippedtime = (time.strip()[2:]).split("-") #removes space, removes DD,splits by -. This forms a list in the format [XXXXAM, YYYYAM] Where x is start, y is end
					starttime = (strippedtime[0]).strip()
					endtime = (strippedtime[1]).strip()
					if len(starttime) < 7:
						starttime = "0"+starttime
					if len(endtime) < 7:
						endtime = "0"+endtime

					starttime = strippeddate + " " + starttime
					endtime = strippeddate + " " + endtime

					getlocation = row.find("span",{'id':re.compile(r'(MTG_LOC\$)([0-9]{1})')})
					if not getlocation.text.strip():
						getlocation = row.find("span",{'id':re.compile(r'(MTG_LOC\$)([0-9]{1})([0-9]{1})')})

					location = getlocation.text

					rowid = (((getlocation.get('id')).split("$"))[1]).strip()
					list_of_class_type_keys = list(class_type_dict.keys())
					list_of_class_type_keys = sorted(list_of_class_type_keys)
					no_of_keys = len(list_of_class_type_keys)
					trigger = "true"
					actual_class_type = ""
					counter = 0
					while trigger == "true":
						actual_class_type = ""
						if int(rowid) >= int(list_of_class_type_keys[counter]):
							actual_class_type = class_type_dict[list_of_class_type_keys[counter]]
							counter += 1
							if counter >= (no_of_keys):
								trigger = "false"				
						else:
							trigger = "false"
					resultdict = {"class_name":subjectitlename,"date":strippeddate,"Start_Time":starttime,"End_Time":endtime,"Location":location,"Type":actual_class_type}
					list_of_results.append(resultdict)
			return(list_of_results)
			driver.close()
		else:
			driver.close()
			return []
