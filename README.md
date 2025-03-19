# TGR Tracker Helper

This is a Discord bot that adds a bunch of tools to trivialize some tasks for Officers within TGR.

This bot interacts with the Google Spreadsheets API, which allows for near full automation for some tasks, like applying quota strikes to members or adding EP, all within some simple Discord commands.

## Installation

The build for this project comes with a missing file you'll have to create (I'll get around to simplifying this later, but it's easy enough to do for now). To get started, create a new text file named "credentials.py". This file will hold two things: Your Google Bot Service Account key, and your Discord Bot key. If you don't know how to get these, I recommend checking out both the [Google Cloud Documentation](https://cloud.google.com/iam/docs/keys-create-delete) and the [Discord Developer Portal](https://discord.com/developers/applications). To add the keys to the file, simply write `botKey = 'Your key'` for the Discord Bot key, and in a new line write `serviceAccountKey = {Your service account key}`. Once you've done that, you can run the bot by executing the `bot_init.py` file.

## IMPORTANT
This bot was made with the 212th Attack Battalion tracker in mind, if you wish to personalize it to suit your division, contact me.

### Configuration

There are some parameters you should change to use this bot, which are located in the `config.py` file.

`guildIDtoSet` = Your Discord server ID
`sheetID` = The Google Sheet ID that the bot is going to interact with.
`DEFAULT_WORKSHEET` The default worksheet name that the bot is gonna use if no "Company" name is provided.
`CLEARANCE_LEVELS` The required role names to run some of the commands. Change as needed. The standard is 1 for normal troopers, 2 for officers, 3 for senior officers, 4 for HICOM.

**Make sure to add your bot service account email as an Editor to the sheet you want it to interact with.**

## Tools

The bot comes with 5 different commands.

`/add_event (@Member) [Company]` (CLEARANCE REQUIRED 2) = Adds an event point to the specified user's Total, weekly, and company rows in the sheet.
`/add_user (@Member) [Company]` (CLEARANCE REQUIRED 3) = Adds the specified member *with their current nickname* to the Sheet, populating their join date as well.
`/fetch_data (@Member) [Company]` (CLEARANCE REQUIRED 1) = Gets some relevant data from the user, such as their strikes, EP, username, join date, etc.
`quota_check [Company]` (CLEARANCE REQUIRED 4) = Runs the quota check, adding strikes if necessary and setting weekly events attended to 0.
`/remove_user (@Member) [Company]` (CLEARANCE REQUIRED 4) = Removes the user's row from the tracker.


## To-do:
- Add commands for logging discharges, punishments, promotions and strikes.
- Expand configuration
- Ease of access

## Final words
This work is a work in progress, new features will be added as time goes on and as they're needed. If you need an adaptation of this bot, or a feature, feel free to request it.
