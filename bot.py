#! /usr/bin/env python3
#-*- coding: utf-8 -*-
##
# Cronus init 
# Written by xlanor
##

import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler,Job, MessageHandler, Filters, RegexHandler, ConversationHandler
from tokens import Tokens
from commands import Commands
from commands import NAME,USERNAME,PASSWORD,KEY,ENTERKEY,DECRYPT,DELETEUSER


def Cronus():
	print('Cronus online')
	updater = Updater(token=Tokens.bot_token('live'))
	dispatcher = updater.dispatcher
	start_handler = CommandHandler('test', Commands.test)
	dispatcher.add_handler(start_handler)
	start_handler = CommandHandler('mega', Commands.mega)
	dispatcher.add_handler(start_handler)
	start_handler = CommandHandler('timetable', Commands.timetable)
	dispatcher.add_handler(start_handler)
	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('register', Commands.register)],

		states={
			NAME: [MessageHandler(Filters.text,Commands.name)],
			USERNAME: [MessageHandler(Filters.text,Commands.username,pass_user_data=True)],
			PASSWORD: [MessageHandler(Filters.text,Commands.password,pass_user_data=True)],
			KEY: [MessageHandler(Filters.text,Commands.keys,pass_user_data=True)]
		},

		fallbacks=[CommandHandler('cancel', Commands.cancel)],
		per_user = 'true'
	)
	dispatcher.add_handler(conv_handler,1)
	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('update', Commands.update)],

		states={
			ENTERKEY: [RegexHandler('(?iii)Yes', Commands.enterkey),RegexHandler('(?iii)No', Commands.cancel)],
			DECRYPT: [MessageHandler(Filters.text,Commands.decrypt)],
		},
		fallbacks=[CommandHandler('cancel', Commands.cancel)],
		per_user = 'true'
	)
	dispatcher.add_handler(conv_handler,2)
	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('forget', Commands.forget)],

		states={
			DELETEUSER: [RegexHandler('(?iii)Yes', Commands.deleteuser),RegexHandler('(?iii)No', Commands.cancel)]
		},
		fallbacks=[CommandHandler('cancel', Commands.cancel)],
		per_user = 'true'
	)
	dispatcher.add_handler(conv_handler,3)
	updater.dispatcher.add_handler(CallbackQueryHandler(Commands.callback))
	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	Cronus()