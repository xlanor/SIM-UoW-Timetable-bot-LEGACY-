#! /usr/bin/env python3
#-*- coding: utf-8 -*-
##
# Cronus commands
# Written by xlanor
##
import pymongo, traceback, calendar
import time as clock
from datetime import datetime,timedelta,date,time
from pymongo import MongoClient
from tokens import Tokens
from telegram import ReplyKeyboardMarkup,ChatAction,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler,Job,ConversationHandler
from modules.testlogin import loginTest
from modules.encryption import Encrypt
from modules.riptimetable import SIMConnect

NAME,USERNAME,PASSWORD,KEY,ENTERKEY,DECRYPT,DELETEUSER = range(7) #declares states for hermes. Imported in main folder
class Commands():
	def mega(bot,update):
		try:
			with MongoClient(Tokens.mongo('live')) as client:
				db = client.timetable
				uid = update.message.from_user.id
				message = update.message.text[6:]
				uid = int(uid)
				checkadmin = Tokens.admin(uid)
				if checkadmin == "admin":
					document = db.timetable.distinct("telegram_id",{"telegram_id":{"$exists":"true"}})
					for each in document:
						user_id = int(each)
						bot.sendMessage(chat_id=user_id, text=message,parse_mode='HTML')
						clock.sleep(0.5)
				else:
					errormessage = "Hey, you don't look like my creator!"
					update.message.reply_text(errormessage,parse_mode='HTML')
		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')

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
			return ConversationHandler.END

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
			return ConversationHandler.END

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
			return ConversationHandler.END

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
			return ConversationHandler.END

	def keys(bot,update,user_data):
		try:
			with MongoClient(Tokens.mongo('live')) as client:
				db = client.timetable
				bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
				uid = update.message.from_user.id
				encryptionkey = update.message.text
				encryptionkey = encryptionkey.strip()
				if len(encryptionkey) <= 16:
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
				else:
					if not encryptionkey:
						message = "Please enter an encryption key."
					else:
						message = "Please enter an encryption key that is under 17 characters."
					update.message.reply_text(message,parse_mode='HTML')
					return KEY

		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')
			return ConversationHandler.END

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
			return ConversationHandler.END

	def enterkey(bot,update):
		try:
			message = "Please enter your decryption key\n"
			update.message.reply_text(message,parse_mode='HTML')
			return DECRYPT
		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')
			return ConversationHandler.END

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
				if not encryptionkey.strip():
					message = "Please enter a proper key!"
					bot.sendMessage(chat_id = update.message.chat_id, text=message,parse_mode='HTML')
					return DECRYPT
				else:
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
			return ConversationHandler.END

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
					previous_start_date = start_date-timedelta(days=7)
					previous_end_date = end_date - timedelta(days=7)
					next_start_date = start_date+timedelta(days=7)
					next_end_date = end_date + timedelta(days=7)
					classes = db.timetable.find_one({"telegram_id":uid},{"class_name":1,"_id":0})
					previous_date_trigger = ""
					next_date_trigger = ""
					for each in classes['class_name']:
						if start_date <= each['date'] <=end_date:
							this_week_classes.append({"name":each['name'],
													"type":each['type'],
													"start_time":each['start_time'],
													"end_time":each['end_time'],
													"location":each['location'],
													"date":each['date']})
						if previous_start_date <= each['date'] <= previous_end_date:
							previous_date_trigger = 'pr'+ datetime.strftime(previous_start_date,'%b%d%Y')

						if next_start_date <= each['date'] <= next_end_date:
							next_date_trigger = 'nx'+datetime.strftime(next_start_date,'%b%d%Y')

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
						keyboard = []
						if previous_date_trigger != "":
							if next_date_trigger != "":
								keyboard.append([InlineKeyboardButton("Previous Week", callback_data=previous_date_trigger),InlineKeyboardButton("Next Week",callback_data=next_date_trigger)])
							else:
								keyboard.append([InlineKeyboardButton("Previous Week", callback_data=previous_date_trigger)])
						else:
							if next_date_trigger != "":
								keyboard.append([InlineKeyboardButton("Next Week", callback_data=next_date_trigger)])

						reply_markup = InlineKeyboardMarkup(keyboard)
						bot.sendMessage(chat_id=update.message.chat_id,reply_markup=reply_markup,text=message,parse_mode='HTML')
						
					else:
						if (previous_date_trigger != "") or (next_date_trigger != "") :
							message = "📈 Timetable for the week of <b>"
							message += datetime.strftime((date.today()-timedelta(days=current_date.weekday())),'%b %d %Y')
							message += "</b>\n"
							message += "🔃 This timetable was last synced on <b>"
							message += datetime.strftime(document['last_synced_date'], '%b %d %Y %H:%M')
							message += "H</b>\n"
							message += "By using this bot, you agree to the terms and conditions stated in the DISCLAIMER.md on github\n\n"
							keyboard = []
							if previous_date_trigger != "":
								if next_date_trigger != "":
									keyboard.append([InlineKeyboardButton("Previous Week", callback_data=previous_date_trigger),InlineKeyboardButton("Next Week",callback_data=next_date_trigger)])
								else:
									keyboard.append([InlineKeyboardButton("Previous Week", callback_data=previous_date_trigger)])
							else:
								if next_date_trigger != "":
									keyboard.append([InlineKeyboardButton("Next Week", callback_data=next_date_trigger)])
							message += "You have no classes this week!"
							reply_markup = InlineKeyboardMarkup(keyboard)
							bot.sendMessage(chat_id=update.message.chat_id,reply_markup=reply_markup,text=message,parse_mode='HTML')
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
			return ConversationHandler.END

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
			return ConversationHandler.END
	def callback(bot,update):
		try:
			with MongoClient(Tokens.mongo('live')) as client:
				query = update.callback_query
				callbacktype = query.data[:2]
				db = client.timetable
				uid = update.callback_query.from_user.id
				document = db.timetable.find_one({"telegram_id":uid})
				if document is not None:
					this_week_classes = []
					current_date = datetime.strptime(query.data[2:],'%b%d%Y')
					start_date = current_date -timedelta(days=current_date.weekday())
					end_date = start_date+timedelta(days=6)
					previous_start_date = start_date-timedelta(days=7)
					previous_end_date = end_date - timedelta(days=7)
					next_start_date = start_date+timedelta(days=7)
					next_end_date = end_date + timedelta(days=7)
					classes = db.timetable.find_one({"telegram_id":uid},{"class_name":1,"_id":0})
					previous_date_trigger = ""
					next_date_trigger = ""
					for each in classes['class_name']:
						try:
							if start_date <= each['date'] <=end_date:
								this_week_classes.append({"name":each['name'],
														"type":each['type'],
														"start_time":each['start_time'],
														"end_time":each['end_time'],
														"location":each['location'],
														"date":each['date']})
							elif previous_start_date <= each['date'] <= previous_end_date:
								previous_date_trigger = 'pr'+ datetime.strftime(previous_start_date,'%b%d%Y')

							elif next_start_date <= each['date'] <= next_end_date:
								next_date_trigger = 'nx'+datetime.strftime(next_start_date,'%b%d%Y')
						except:					
							catcherror = traceback.format_exc()
							bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')
					if this_week_classes:
						this_week_classes = sorted(this_week_classes, key=lambda item:item['start_time'])
						message = "📈 Timetable for the week of <b>"
						message += datetime.strftime((current_date-timedelta(days=current_date.weekday())),'%b %d %Y')
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
						keyboard = []
						if previous_date_trigger != "":
							if next_date_trigger != "":
								keyboard.append([InlineKeyboardButton("Previous Week", callback_data=previous_date_trigger),InlineKeyboardButton("Next Week",callback_data=next_date_trigger)])
							else:
								keyboard.append([InlineKeyboardButton("Previous Week", callback_data=previous_date_trigger)])
						else:
							if next_date_trigger != "":
								keyboard.append([InlineKeyboardButton("Next Week", callback_data=next_date_trigger)])

						reply_markup = InlineKeyboardMarkup(keyboard)
						bot.edit_message_text(text=message,chat_id=update.callback_query.message.chat_id,message_id=update.callback_query.message.message_id,reply_markup=reply_markup,parse_mode='HTML')
					else:
						if (previous_date_trigger != "") or (next_date_trigger != "") :
							message = "📈 Timetable for the week of <b>"
							message += datetime.strftime((date.today()-timedelta(days=current_date.weekday())),'%b %d %Y')
							message += "</b>\n"
							message += "🔃 This timetable was last synced on <b>"
							message += datetime.strftime(document['last_synced_date'], '%b %d %Y %H:%M')
							message += "H</b>\n"
							message += "By using this bot, you agree to the terms and conditions stated in the DISCLAIMER.md on github\n\n"
							keyboard = []
							if previous_date_trigger != "":
								if next_date_trigger != "":
									keyboard.append([InlineKeyboardButton("Previous Week", callback_data=previous_date_trigger),InlineKeyboardButton("Next Week",callback_data=next_date_trigger)])
								else:
									keyboard.append([InlineKeyboardButton("Previous Week", callback_data=previous_date_trigger)])
							else:
								if next_date_trigger != "":
									keyboard.append([InlineKeyboardButton("Next Week", callback_data=next_date_trigger)])
							message += "You have no classes this week!"
							reply_markup = InlineKeyboardMarkup(keyboard)
							bot.sendMessage(chat_id=update.message.chat_id,reply_markup=reply_markup,text=message,parse_mode='HTML')
						else:
							message = "No timetable could be retrieved."
							update.message.reply_text(message,parse_mode='HTML')

				else:
					message = "Unable to find a timetable tied to this telegram id \n"
					message += "Please use /register to register your account."
					update.message.reply_text(message,parse_mode='HTML')
		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')

	def unsubreminder(bot,update):
		try:
			with MongoClient(Tokens.mongo('live')) as client:
				db = client.timetable
				uid = update.message.from_user.id
				checksub = db.timetable.find({"telegram_id":uid})
				if not checksub:
					message = "We can't unsubscribe from what doesn't exist!\n Are you registered in our database?"
				else:
					db.timetable.update({"telegram_id":uid},{"$set":{"alert":"false"}})
					message = "Sucessfully unsubscribed. To resubscribe, use /alert"
				update.message.reply_text(message,parse_mode='HTML')
		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')

	def togglenightly(bot,update):
		try:
			with MongoClient(Tokens.mongo('live')) as client:
				db = client.timetable
				uid = update.message.from_user.id
				checksub = db.timetable.find_one({"telegram_id":uid})
				if not checksub:
					message = "We can't unsubscribe from what doesn't exist!\n Are you registered in our database?"
				else:
					if 'nightly_alert' in checksub:
						if checksub['nightly_alert'] == "true":
							db.timetable.update({"telegram_id":uid},{"$set":{"nightly_alert":"false"}})
							message = "Sucessfully unsubscribed from nightly updates. To resubscribe, use /nightly"
						else:
							db.timetable.update({"telegram_id":uid},{"$set":{"nightly_alert":"true"}})
							message = "Sucessfully subscribed to nightly updates. To unsubscribe, use /nightly"
					else:
						db.timetable.update({"telegram_id":uid},{"$set":{"nightly_alert":"true"}})
						message = "Sucessfully subscribed to nightly updates. To unsubscribe, use /nightly"


				update.message.reply_text(message,parse_mode='HTML')
		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')

	def subscribereminder(bot,update):
		try:
			with MongoClient(Tokens.mongo('live')) as client:
				db = client.timetable
				uid = update.message.from_user.id
				checksub = db.timetable.find({"telegram_id":uid})
				if not checksub:
					message = "We can't subscribe to what doesn't exist!\n Are you in our database?"
				else:
					db.timetable.update({"telegram_id":uid},{"$set":{"alert":"true"}})
					message = "Sucessfully subscribed. To unsubscribe, use /unsub"
				update.message.reply_text(message,parse_mode='HTML')
		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')

	def reminder(bot,update):
		try:
			with MongoClient(Tokens.mongo('live')) as client:
				db = client.timetable
				timetablelist = db.timetable.find()
				for each in timetablelist:
					if 'alert' in each:
						if each['alert'] == "true":
							message = "Good Morning, "
							message += each['name']
							message += "\n"
							message += "These are your classes for today, "
							message += datetime.strftime(datetime.now(),'%b %d %Y')
							message += "\n"
							message += "\n📅 "
							message += datetime.today().strftime("%A")
							classeslist = []
							today_class = db.timetable.find_one({"telegram_id":each['telegram_id']},{'class_name':1,'_id':0})
							for classes in today_class['class_name']:
								if (classes['date'].date()) == datetime.now().date():
									classeslist.append({"name":classes['name'],
														"type":classes['type'],
														"location":classes['location'],
														"start_time":classes['start_time'],
														"end_time":classes['end_time']
														})
							if not classeslist:
								message += "\n-"
								message += "\n\n"
								message += "To unsubscribe from this daily reminder, use /unsub\n"
							else:
								classeslist = sorted(classeslist, key=lambda item:item['start_time'])
								for retrieved_classes in classeslist:
									message += "\n"
									message += retrieved_classes['name']
									message += "\nDate: <b>"
									message += datetime.strftime(datetime.now().date(),'%b %d %Y')
									message += "</b>\n"
									message += "Type: "
									message += retrieved_classes['type']
									message += "\nLocation: "
									message += retrieved_classes['location']
									message += "\nStart Time: "
									message += datetime.strftime(retrieved_classes['start_time'],'%H:%M')
									message += "\n"
									message += "End Time :"
									message += datetime.strftime(retrieved_classes['end_time'],'%H:%M')
									
							
								message += "\n\n"
								message += "To unsubscribe from this daily reminder, use /unsub\n"
							bot.sendMessage(chat_id=each['telegram_id'], text=str(message),parse_mode='HTML')


		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')

	def nightlyreminder(bot,update):
		try:
			with MongoClient(Tokens.mongo('live')) as client:
				db = client.timetable
				timetablelist = db.timetable.find()
				earlymessage = "You have an early class tomorrow, <b>please sleep early tonight!</b>"
				earlytimestart = datetime.strptime("08:00","%H:%M")
				earlytimeend = datetime.strptime("11:00","%H:%M")
				for each in timetablelist:
					if 'nightly_alert' in each:
						if each['nightly_alert'] == "true":
							earlytrigger = 0
							message = "Good evening, "
							message += each['name']
							message += "\n"
							message += "These are your classes for <b>tomorrow</b>, "
							message += datetime.strftime((datetime.now())+timedelta(1),'%b %d %Y')
							message += "\n"
							message += "\n📅 <b>"
							message += ((datetime.today())+timedelta(1)).strftime("%A")
							message += "</b>"
							classeslist = []
							today_class = db.timetable.find_one({"telegram_id":each['telegram_id']},{'class_name':1,'_id':0})
							for classes in today_class['class_name']:
								if (classes['date'].date()) == ((datetime.now())+timedelta(1)).date():
									classeslist.append({"name":classes['name'],
														"type":classes['type'],
														"location":classes['location'],
														"start_time":classes['start_time'],
														"end_time":classes['end_time']
														})
							if not classeslist:
								message += "\n-"
								message += "\n\n"
								message += "To unsubscribe from this daily reminder, use /unsub\n"
							else:
								classeslist = sorted(classeslist, key=lambda item:item['start_time'])
								for retrieved_classes in classeslist:
									message += "\n"
									message += retrieved_classes['name']
									message += "\nDate: <b>"
									message += datetime.strftime(((datetime.now())+timedelta(1)).date(),'%b %d %Y')
									message += "</b>\n"
									message += "Type: "
									message += retrieved_classes['type']
									message += "\nLocation: "
									message += retrieved_classes['location']
									message += "\nStart Time: "
									message += datetime.strftime(retrieved_classes['start_time'],'%H:%M')
									if (earlytimestart.time() <= retrieved_classes['start_time'].time() <= earlytimeend.time()):
										earlytrigger += 1

									message += "\n"
									message += "End Time :"
									message += datetime.strftime(retrieved_classes['end_time'],'%H:%M')

									if earlytrigger > 0:
										message += "\n"
										message += earlymessage
									
							
								message += "\n\n"
								message += "To unsubscribe from this nightly reminder, use /nightly\n"
							bot.sendMessage(chat_id=each['telegram_id'], text=str(message),parse_mode='HTML')
						


		except:
			catcherror = traceback.format_exc()
			bot.sendMessage(chat_id=Tokens.channel('errorchannel'), text=str(catcherror),parse_mode='HTML')


if __name__ == "__main__":
	Commands.nightlyreminder()