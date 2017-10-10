# Cronus

Working name: Cronus

A telegram bot for ripping timetables from SIM Connect built in python3

This bot is **not** an official bot sanctioned by either the University of Wollongong or the Singapore Institute of Management.

Please read the [Disclaimer](DISCLAIMER.md) before proceeding.

## Why?

![Why?](https://i.imgur.com/7b3GTNU.png "Why?")

And also to familarize myself with mongoDB

## Encryption

**I strongly encourage users to run their own instance of this bot instead of relying on the one I'm hosting.**

However, if you're using the instance that I am hosting, please read the following sentence

Although you are asked to enter your login credentials, At no point of time whatsoever does Cronus store your password **in plaintext** to the database.

Cronus encrypts your password with a key of your choice with AES-256 and requires the key to decrypt the password each time it syncs. The module can be found under modules/encryption.py

The stored password is the **encrypted text**. The key is kept by **you**. This is why you will need to enter the key each time to decrypt it on sync.

You are free to audit the source code.

You should take note that this is not the most secure method, but is the most convenient method for users.

As such, I strongly reccomend that you do not reuse your SIM Connect password anywhere else should you use this instance.

I am not responsible for any damages incurred from the usage of this bot.


## Licensing

Cronus is licensed under the [GNU Affero General Public License v3](LICENSE).

All derivatives works not intended for personal use must be released into the public domain for the sake of transparency


## Usage

A sample of Cronus is up on telegram at [SIM-UoW Timetable Bot](https://t.me/Uow_sim_tt_bot)

**Due to the sensitive nature of the bot, I strongly encourage users to run their own instance of this bot instead of relying on the one I'm hosting.**

This bot has only been tested on student University of Wollongong Timetables that are currently going through a 2 module trimester.

You may proceed to use it for other timetables, but at your own risk.

* /register to register your credentials with the bot
* /update to perform a full timetable sync
* /timetable to retrieve your timetable for the week previously generated by the sync
* /forget to wipe your details from the bot.

## Future

Currently, I'm working on these features

* Scroll through your timetable - see the next week's, previous weeks, etc
* A module to calculate the number of classes that you've been absent for and tell you how many more classes you can skip (unsure if this can be done)


## Credits
* [Python-Telegram-Bot](https://github.com/python-telegram-bot/python-telegram-bot)
* [Selenium](https://pypi.python.org/pypi/selenium)
* [PhantomJS](https://bitbucket.org/ariya/phantomjs/downloads/)
* [BeautifulSoup4](https://code.launchpad.net/beautifulsoup/)

## F.A.Q

**What is a "Key?"**

Like the name suggests, a key is used to unlock a lock. In this case, a key is used to unlock the encrypted password. It can be any alphanumeric string you want.

**But you're stealing my passwords!**

Read above section regarding encryption and **running your own local instance**

**When do I need to sync? Do I sync it weekly?**

You only need to sync your timetable when theres an update to your timetable. ie: New semester, change of venue.
Other than that, the bot should detect the current day of the week and pull the entire week's timetable automatically with /timetable.

**Your bot sucks! It didnt tell me that I had a class and I missed it!**

Read the disclaimer, and notify me so that I can fix the bug.

**I read the output wrongly and missed my class!**

User Problem.


## Contact

Open an issue on github or contact me on telegram at @fatalityx