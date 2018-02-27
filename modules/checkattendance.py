#! /usr/bin/env python3
#-*- coding: utf-8 -*-
##
# Cronus module check tiemtable. from SIM connect
# Written by xlanor
##
import time as clock
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from contextlib import closing
from bs4 import BeautifulSoup
import re
class checkAttendance():
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

	def checkatt(self,username,password):
		student_center_url = 'https://simconnect.simge.edu.sg/psp/paprd_2/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL'
		driver = webdriver.PhantomJS(executable_path='./phantomjs',service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
		driver.set_window_size(1124, 850) 
		page_source = self.login(username,password,driver)
		if 'https://simconnect.simge.edu.sg/psp/paprd/EMPLOYEE/EMPL/?cmd=logout' in page_source:
			return self.navigate_attendance(driver,student_center_url)
		else:
			return []

	def navigate_attendance(self,driver,student_center_url):
		driver.get(student_center_url)
		clock.sleep(10)

		# find the iframe
		frame = driver.find_element_by_id("ptifrmtgtframe")
		# switch to iframe.
		driver.switch_to.frame(frame)
		#at student center page, click drop down
		select = Select(driver.find_element_by_id("DERIVED_SSS_SCL_SSS_MORE_ACADEMICS"))
		select.select_by_value('4030') #4030 is the value of the attendence selection.
		clock.sleep(10)
		gobtn = driver.find_element_by_id('DERIVED_SSS_SCL_SSS_GO_1')
		gobtn.click()
		clock.sleep(10)
		#formatted_result = driver.page_source
		#soup = BeautifulSoup(formatted_result,"html.parser")
		returndict = {}
		self.grab_initial_info(returndict,driver)
		if not self.get_attendance(driver,returndict):
			print ("float conversion error")
		return returndict

	def log_source_for_debug(self,driver):
		formatted_result = driver.page_source
		with open("logging.txt","w") as log:
			log.write(formatted_result)

	def grab_initial_info(self,returndict,driver):
		formatted_result = driver.page_source
		soup = BeautifulSoup(formatted_result,"html.parser")
		icaspan = soup.find('span',{'id':'SM_CUSTOM_WRK_DESCR50$0'})
		returndict['ICA attendance'] = icaspan.text if icaspan else "N/A"
		simglobalspan = soup.find('span',{'id':'SM_CUSTOM_WRK_DESCR50$1'})
		returndict['SIM Global'] = simglobalspan.text if simglobalspan else "N/A"
		partnerspan = soup.find('span',{'id':'SM_CUSTOM_WRK_DESCR50$2'})
		returndict['Partner Uni attendance'] = partnerspan.text
		uniname = soup.find('span',{'id':'INSTITUTION_TBL_DESCR'})
		returndict['University'] = uniname.text
		termname = soup.find('span',{'id':'TERM_TBL_DESCR'})
		returndict['Term'] = termname.text
		programname = soup.find('span',{'id':'SM_STUDENT_TERM_DESCR'})
		returndict['Program'] = programname.text

	def get_attendance(self,driver,returndict):
		try:
			att = float(returndict['Partner Uni attendance'])
		except ValueError:
			return False
		else:#win2divCLASSES$0
			if float(att) != 100.00:
				formatted_result = driver.page_source
				soup = BeautifulSoup(formatted_result,"html.parser")
				classes = soup.findAll('span',{'id':re.compile(r'(CLASSES\$span\$)([0-9]{1})')})
				lastindex = len(classes)-1
				print(lastindex)
				while lastindex >= 0:
					self.navigate_classes(driver,returndict,lastindex)
					lastindex -= 1

			return True

	def navigate_classes(self,driver,returndict,index):
		classid = "SM_STDNT_CLASS$sels$"+str(index)+"$$0"
		classbtn =  driver.find_element_by_id(classid)
		classbtn.click()
		continuebtn = driver.find_element_by_id("SM_CUSTOM_WRK_SSR_PB_GO")
		continuebtn.click()
		clock.sleep(10)
		#we are now in the class. lets find the attendance.
		no_classes = self.getnoclasses(driver)
		counter = 0
		while counter < no_classes:
			attid = "SM_CUSTOM_WRK_SM_ATTEND_PRESENT$"+str(counter)
			attdateid = "SM_CLS_ATND_VW4_CLASS_ATTEND_DT$"+str(counter)
			attstarttime = "SM_CLS_ATND_VW4_ATTEND_FROM_TIME$"+str(counter)
			present = driver.find_element_by_id(attid)
			if present.text == "No":
				try:
					len(returndict['Absent'])
				except KeyError:
					returndict['Absent'] = []
				#SM_CLS_ATND_VW4_CLASS_ATTEND_DT$
				class_name = driver.find_element_by_id("DERIVED_SSR_FC_SSR_CLASSNAME_LONG$span").text
				date_of_absence = driver.find_element_by_id(attdateid).text
				start_time = driver.find_element_by_id(attstarttime).text
				returndict['Absent'].append({"name":class_name,"date":date_of_absence,"time":start_time})
			counter +=1

		backtbtn = driver.find_element_by_id("SM_CUSTOM_WRK_SSS_CHG_CLS_LINK")
		backtbtn.click()
		clock.sleep(10)

	def getnoclasses(self,driver):
		total_class = 0
		formatted_result = driver.page_source
		soup = BeautifulSoup(formatted_result,"html.parser")

		no_classes = soup.findAll('span',{'id':re.compile(r'(SM_CLS_ATND_VW4_CLASS_ATTEND_DT\$)([0-9]{1})')})
		if len(no_classes) > 0:
			no_classes_2 = soup.find("span",{"id":re.compile(r'(SM_CLS_ATND_VW4_CLASS_ATTEND_DT\$)([0-9]{1})([0-9]{1})')})

		try:
			total_class += len(no_classes)
		except TypeError:
			pass
		except ValueError:
			pass

		try:
			total_class += len(no_classes_2)
		except TypeError:
			pass
		except ValueError:
			pass

		return total_class
		
