# Discord Bot for deadlines
Desiged by Ciaran for the Heriot Watt year 2 discord server

## Commands

- `.all` will display all the current deadlines
- `.thisweek` will display all deadlines this week
- `.past` will display deadlines that are in the past
- `.upcoming` will show all deadlines which have not finished
- `.next` will show the next deadline


## How to run the bot
1. clone the repository

2. cd into the repository directory

3. then pip install the requirements - you can set up a virtual environment as well

    `pip install -r requirements.txt`

4. Give the bot your discord token and channel to announce with, with these commands - needs to be run every time you restart your console

    `export DISCORD_TOKEN="your discord token here"`

    `export ANNOUNCE_CHANNEL="Channel ID"`

5. Then run the bot with

    `python3 src/main.py`