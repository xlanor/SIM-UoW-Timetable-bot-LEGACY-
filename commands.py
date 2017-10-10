#! /usr/bin/env python3
#-*- coding: utf-8 -*-
##
# Cronus commands
# Written by xlanor
##
import pymongo, traceback,time, calendar
from datetime import datetime,timedelta,date,time
from pymongo import MongoClient
from tokens import Tokens
from telegram import ReplyKeyboardMarkup,ChatAction
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler,Job,ConversationHandler
from modules.testlogin import loginTest
from modules.encryption import Encrypt
from modules.riptimetable import SIMConnect

NAME,USERNAME,PASSWORD,KEY,ENTERKEY,DECRYPT,DELETEUSER = range(7) #declares states for hermes. Imported in main folder
class Commands():

	def register(bot,update):
		try:
			with MongoClient(Tokens.mongo('live')) as client:
				db = client.timetable
				uid = update.message.from_user.id
				find_userid = db.timetable.find_one({"telegram_id":uid})
				if find_userid is None:
					db.timetable.insert_one({'telegram_id':uid})
					message = "Hi! Let's get started by registering with this bot\n"
					message += "By using this bot, you hereby declare that you have read the documentation and disclaimer on github.\n"
					message += "As such, you release the author from any responsibilities of events incurred by the usage of this bot\n"
					message += "At any point of time during this process, you can stop the bot by typing /cancel\n"
					message += "Now, can I have your name?"
					update.message.reply_text(message,parse_mode='HTML')
					return NAME

				else:
					message = "You seem to have already been registered\n"
					message += "If you've forgotten your secret key, please use /forget to clear your information and re-register."
					update.message.reply_text(message,parse_mode='HTML')
					return ConversationHandler.END
		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')

	def name(bot,update):
		try:
			with MongoClient(Tokens.mongo('live')) as client:
				db = client.timetable
				uid = update.message.from_user.id
				name = update.message.text
				db.timetable.update({"telegram_id":uid},
									{"$set":{"name":name}})
				message = "Now, may I have your user ID?"
				update.message.reply_text(message,parse_mode='HTML')
				return USERNAME
		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')

	def username(bot,update,user_data):
		try:
			uid = update.message.from_user.id
			username = update.message.text
			user_data['username'] = username
			message = "Now, may I have your password?\n"
			message += "For more information about how your password is stored, please read my github."
			update.message.reply_text(message,parse_mode='HTML')
			return PASSWORD
		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')

	def password(bot,update,user_data):
		try:
			uid = update.message.from_user.id
			username = user_data['username']
			password = update.message.text
			waitingmsg = "Currently testing your creditentials, please wait.."
			bot.sendMessage(chat_id=update.message.chat_id, text=waitingmsg,parse_mode='HTML')
			bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
			testresult = loginTest().testlogin(username,password)
			if testresult == "false":
				user_data.clear()
				msg = "Oops. Looks like you've given us a wrong username and/or password\n"
				msg += "Lets try that again.\n"
				msg += "Please enter your username.\n"
				bot.sendMessage(chat_id=update.message.chat_id, text=msg,parse_mode='HTML')
				return USERNAME
			else:
				user_data['password'] = password
				message = "Now, I need you to pick a key to encrypt your password with.\n"
				message += "This key will be case-sensetive and stripped of all spaces.\n"
				message += "Do not forget your key.\n"
				update.message.reply_text(message,parse_mode='HTML')
				return KEY
		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')

	def keys(bot,update,user_data):
		try:
			with MongoClient(Tokens.mongo('live')) as client:
				db = client.timetable
				bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
				uid = update.message.from_user.id
				encryptionkey = update.message.text
				encryptionkey = encryptionkey.strip()
				password = user_data['password']
				encrypted = Encrypt().encrypt(password,encryptionkey,"encrypt")
				db.timetable.update({"telegram_id":uid},
									{"$set":{"user_name":user_data['username'],
											 "encrypted_pass":encrypted}
									})
				message = "Sucessfully encrypted and stored your details\n"
				message += "You may now use /update to get your timetable."
				update.message.reply_text(message,parse_mode='HTML')
				user_data.clear()
				return ConversationHandler.END

		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')

	def update(bot,update):
		try:
			message = "Do you want to update your timetable?\n"
			message += "This will erase all previously retrieved timetable schedules\n"
			message += "Please reply with a yes or no (case-insensetive)"
			update.message.reply_text(message,parse_mode='HTML')
			return ENTERKEY

		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')

	def enterkey(bot,update):
		try:
			message = "Please enter your decryption key\n"
			update.message.reply_text(message,parse_mode='HTML')
			return DECRYPT
		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')

	def decrypt(bot,update):
		try:
			with MongoClient(Tokens.mongo('live')) as client:
				waitingmsg = "Currently decrypting and logging in \n"
				waitingmsg += "This process can take up to 2 minutes\n"
				waitingmsg += "Please wait.."
				bot.sendMessage(chat_id=update.message.chat_id, text=waitingmsg,parse_mode='HTML')
				bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
				db = client.timetable
				uid = update.message.from_user.id
				document = db.timetable.find_one({"telegram_id":uid})
				encryptionkey = update.message.text
				if document is not None:
					username = document['user_name']
					encryptedpass = document['encrypted_pass']
					decrypted = Encrypt().encrypt(encryptedpass,encryptionkey,"decrypt")
					if decrypted.strip() != "":
						resultlist = SIMConnect().timetable(username,decrypted)
						if resultlist:
							db.timetable.update({"telegram_id":uid},
										{"$set":{"class_name":[]}
										})
							db.timetable.update({"telegram_id":uid},
										{"$set":{"last_synced_date":datetime.now()}
										})
							for each in resultlist:
								#convert DT to save to mongo.
								class_date = datetime.strptime(each['date'], '%d/%m/%Y')
								class_start = datetime.strptime(each['Start_Time'], '%d/%m/%Y %I:%M%p')
								class_end = datetime.strptime(each['End_Time'], '%d/%m/%Y %I:%M%p')
								db.timetable.update({"telegram_id":uid},
									{"$push":{"class_name":{
											"name":each['class_name'],
											"type":each['Type'],
											"date":class_date,
											"start_time":class_start,
											"end_time":class_end,
											"location":each['Location']}}
									})
							no_results = len(resultlist)
							message = "A total of "
							message += str(no_results)
							message += " records has been synced to the database.\n"
							message += "You may now use /timetable to view your timetable"
							update.message.reply_text(message,parse_mode='HTML')
						else:
							message = "Unable to login \n"
							message += "Are you sure that your credentials are correct? \n"
							message += "Try to update your credentials using /register \n"
							update.message.reply_text(message,parse_mode='HTML')
						return ConversationHandler.END
					else:
						update.message.reply_text("You entered the wrong decryption key, please try again",parse_mode='HTML')
						return DECRYPT
				else:
					message = "Oops, something went wrong \n"
					message += "We're dispatching a team of trained monkeys to look into this"
					update.message.reply_text(decrypted,parse_mode='HTML')
					return ConversationHandler.END

		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')

	def cancel(bot,update):
		#cancels conversation state.
		message = "Did I make you uncomfortable? =(\n"
		message += "Here's a seal for you to play with. Goodbye! (ᵔᴥᵔ)"
		update.message.reply_text(message, parse_mode='HTML')
		return ConversationHandler.END

	def timetable(bot,update):
		try:
			with MongoClient(Tokens.mongo('live')) as client:
				db = client.timetable
				uid = update.message.from_user.id
				document = db.timetable.find_one({"telegram_id":uid})
				if document is not None:
					this_week_classes = []
					current_date = date.today()
					current_date = datetime.combine(current_date, time()) #sets time to midnight.
					start_date = current_date -timedelta(days=current_date.weekday())
					end_date = start_date+timedelta(days=6)
					classes = db.timetable.find_one({"telegram_id":uid},{"class_name":1,"_id":0})
					for each in classes['class_name']:
						if start_date <= each['date'] <=end_date:
							this_week_classes.append({"name":each['name'],
													"type":each['type'],
													"start_time":each['start_time'],
													"end_time":each['end_time'],
													"location":each['location'],
													"date":each['date']})

					if this_week_classes:
						this_week_classes = sorted(this_week_classes, key=lambda item:item['start_time'])
						message = "📈 Timetable for the week of <b>"
						message += datetime.strftime((date.today()-timedelta(days=current_date.weekday())),'%b %d %Y')
						message += "</b>\n"
						message += "🔃 This timetable was last synced on <b>"
						message += datetime.strftime(document['last_synced_date'], '%b %d %Y %H:%M')
						message += "H</b>\n"
						message += "By using this bot, you agree to the terms and conditions stated in the DISCLAIMER.md on github\n\n"
						counter = 0
						while counter <= 6:
							message += "󠁳📅 <b>"
							message += calendar.day_name[counter]
							message += "</b>\n"
							dashmessage = ""
							for classes in this_week_classes:
								if datetime.date(classes['date']).weekday() == counter:
									dashmessage += "<i>"
									dashmessage += classes['name']
									dashmessage += "</i>\n"
									dashmessage += "Date: "
									dashmessage += datetime.strftime(classes['date'],'%b %d %Y')
									dashmessage += "\n"
									dashmessage += "Type: "
									dashmessage += classes['type']
									dashmessage += "\n"
									dashmessage += "Start Time: "
									dashmessage += datetime.strftime(classes['start_time'],'%H:%M')
									dashmessage += "\n"
									dashmessage += "End Time: "
									dashmessage += datetime.strftime(classes['end_time'],'%H:%M')
									dashmessage += "\n"
									dashmessage += "Location: "
									dashmessage += classes['location']
									dashmessage += "\n\n"
							if not dashmessage.strip():
								message += "-\n\n"
							else:
								message += dashmessage
							counter += 1
						update.message.reply_text(message,parse_mode='HTML')
					else:
						message = "No timetable could be retrieved."
						update.message.reply_text(message,parse_mode='HTML')

				else:
					message = "Unable to find a timetable tied to this telegram id \n"
					message += "Please use /register to register your account."
					update.message.reply_text(message,parse_mode='HTML')
					return ConversationHandler.END

		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')

	def test(bot,update):
		bot.sendMessage(chat_id=update.message.chat_id, text='Cronus online',parse_mode='HTML')

	def forget(bot,update):
		try:
			message = "Do you want to erase all your details?\n"
			message += "Please reply with a yes or no (case-insensetive)"
			update.message.reply_text(message,parse_mode='HTML')
			return DELETEUSER
		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')

	def deleteuser(bot,update):
		try:
			with MongoClient(Tokens.mongo('live')) as client:
				db = client.timetable
				uid = update.message.from_user.id
				document = db.timetable.find_one({"telegram_id":uid})
				if document is not None:
					result = db.timetable.delete_one({"telegram_id":uid})
					if result.deleted_count == 1:
						message = "Your details have been wiped!\n"
						message += "You may now use /register to register again"
						update.message.reply_text(message,parse_mode='HTML')
						return ConversationHandler.END
					else:
						message = "Something went wrong!\n"
						message += "Please notify @fatalityx of your issue."
						update.message.reply_text(message,parse_mode='HTML')
						return ConversationHandler.END

				else:
					message = "Your details are not on record with us!\n"
					message += "We can't delete things that don't exist."
					update.message.reply_text(message,parse_mode='HTML')
					return ConversationHandler.END

		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')