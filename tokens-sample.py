#! /usr/bin/env python3
#-*- coding: utf-8 -*-
##
# Cronus tokens, usernames, passwords
# Written by xlanor
##
class Tokens():
	def mongo(x):
		if x == "live":
			return 'mongodb://username:password@server:port/'
	def bot_token(x):
		if x == "live":
			return 'place_your_telegram_bot_token'

	def channel(x):
		if x == "errorchannel":
			return "place_your_error_bot_channel_id"