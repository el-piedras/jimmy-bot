import discord
from discord.ext import commands
from datetime import datetime, timedelta
from utils import *
import credentials
import gspread

## Google Sheets Init
scope = ["https://www.googleapis.com/auth/spreadsheets"]
gc = gspread.service_account_from_dict(credentials.sheetsKey)

sheet_id = "1NhU9tel9pk23uAjVNpxBUUyodA7I-fWInC7TqP6I5AA"
sheet = gc.open_by_key(sheet_id)

trooperSheet = sheet.worksheet("Trooper")

## Discord Bot Init

class Client(commands.Bot):

    async def on_ready(self):
        print(f'Logged in as {client.user}')

        try:
            guild = GUILD_ID
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands to guild {guild.id}')
        except Exception as e:
            print(f'Commands failed to sync: {e}')

intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix=';', intents=intents)

GUILD_ID = discord.Object(id=1341169501315534878)

## App command to add user to the database
@client.tree.command(name="add-user", description="Adds user to the Activity Tracker", guild=GUILD_ID)
async def AddUser(interaction: discord.Interaction, username: discord.Member):

    ## Gets Member object
    userToCheck = await GetInteractionCaller(interaction)

    ## Checks if interaction user has necessary roles
    if not HasClearance(3, userToCheck):
        await interaction.response.send_message(ephemeral=True, content=f"{interaction.user.mention} You don't have permission to run this command.")
        return

    ## Checks if username exists in database
    userToAdd = username.nick or username.global_name or username.name
    userExists = trooperSheet.find(userToAdd, in_column=2)

    ## If user is already in DB, send response and cancel
    if userExists:
        await interaction.response.send_message(ephemeral=True, content=f"{interaction.user.mention} User {username.name} is already on the database.")
        return

    ## Data to insert for new members
    memberDefaultData = [userToAdd, "Recruit", 0, 0, 0, 0, "FALSE", 0, None, str(username.joined_at.date())]

    ## Flag to check if gaps exist  
    foundEmpty = False

    ## Otherwise, gets usernames from the database
    trooperUsernameValue = trooperSheet.get_values("B19:B")
    trooperUsernameValue = [value[0] if value else "" for value in trooperUsernameValue]

    ## If gap is found, populate it first...
    for i, value in enumerate(trooperUsernameValue, start=19):
        if value == "":
            trooperSheet.update(range_name=f"B{i}:K{i}", values=[memberDefaultData], value_input_option="USER_ENTERED")
            foundEmpty = True
            break

        ## Otherwise, generates a new row and populates it
    if not foundEmpty:        
        i + 1 ## Must account index for the newly added row
        trooperSheet.append_row(memberDefaultData, value_input_option="USER_ENTERED")
    
    ## Generates and sends confirmation response
    newEmbed = discord.Embed(title="Added user", color=discord.Color.orange())
    newEmbed.add_field(name="Username", value=userToAdd, inline=True)
    newEmbed.add_field(name="Join date", value=username.joined_at.date(), inline=True)
    newEmbed.add_field(name="Row in Database", value=i, inline=True)
    newEmbed.set_footer(text="212th Attack Battalion Tracker")
    await interaction.response.send_message(embed=newEmbed)


@client.tree.command(name="fetch-data", description="Gets the specified user's join date, events attended and strikes", guild=GUILD_ID)
async def GetUserInfo(interaction: discord.Interaction, user: discord.Member):

    ## Checks if caller has permission
    userToCheck = await GetInteractionCaller(interaction)

    if not HasClearance(1, userToCheck):
        await interaction.response.send_message(ephemeral=True, content=f"{interaction.user.mention} You don't have permission to run this command.")
        return
    
    ## Checks if user is in database
    userToFetch = user.nick or user.global_name or user.name
    usernameCell = trooperSheet.find(userToFetch)

    ## Cancel operation if NOT found
    if not usernameCell:
        await interaction.response.send_message(f"{interaction.user.mention} User was not found in the database.", ephemeral=True)
        return
    
    ## Otherwise, get the values from the row
    rowList = trooperSheet.get(f"B{usernameCell.row}:K{usernameCell.row}")
    flatList = [
        "Yes" if item == "TRUE" else "No" if item == "FALSE" else item for item in rowList[0]
    ]

    ## Generate response...
    newEmbed = discord.Embed(title=f"Database data for {user.mention}", color=discord.Color.orange())
    newEmbed.add_field(name="Username", value=flatList[0])
    newEmbed.add_field(name="Rank", value=flatList[1])
    newEmbed.add_field(name="Events Attended", value=flatList[2])
    newEmbed.add_field(name="Weekly Events Attended", value=flatList[3])
    newEmbed.add_field(name="Events Attended in Current Company", value=flatList[4])
    newEmbed.add_field(name="Quota Strikes", value=flatList[5])
    newEmbed.add_field(name="Inactivity Notice", value=flatList[6])   
    newEmbed.add_field(name="Resets Taken this Month", value=flatList[7])   
    newEmbed.add_field(name="Quota Complete?", value=flatList[8])
    newEmbed.add_field(name="Join Date", value=flatList[9])
    newEmbed.set_footer(text="212th Attack Battalion Tracker")
    await interaction.response.send_message(embed=newEmbed, delete_after=60)

@client.tree.command(name="remove-user", description="Removes the user from the database", guild=GUILD_ID)
async def GetUserInfo(interaction: discord.Interaction, user: discord.Member):

    ## Check if the caller has permissions
    userToCheck = await GetInteractionCaller(interaction)

    if not HasClearance(3, userToCheck):
        await interaction.response.send_message(ephemeral=True, content=f"{interaction.user.mention} You don't have permission to run this command.")
        return

    userToRemove = user.nick or user.global_name or user.name
    usernameCell = trooperSheet.find(userToRemove)

    if not usernameCell:
        await interaction.response.send_message(f"{interaction.user.mention} User not found in database.")
        return
    
    if usernameCell.row == trooperSheet.row_count:
        trooperSheet.delete_rows(usernameCell.row)

    else:
        trooperSheet.update(range_name=f"B{usernameCell.row}:K{usernameCell.row}", values=[["","","0","0","0","0","FALSE","0","FALSE",""]], value_input_option="USER_ENTERED")
    
    await interaction.response.send_message(ephemeral=True, content=f"{interaction.user.mention} User has been successfully removed from the database.")

@client.tree.command(name="quota-check", description="Checks if anyone in the database hasn't completed their quota and applies strike if necessary.", guild=GUILD_ID)
async def CheckQuota(interaction: discord.Interaction):

    ## Check if the caller has permissions
    userToCheck = await GetInteractionCaller(interaction)

    if not HasClearance(3, userToCheck):
        await interaction.response.send_message(ephemeral=True, content=f"{interaction.user.mention} You don't have permission to run this command.")
        return

    data = trooperSheet.batch_get(["G20:G", "H20:H", "J20:J", "K20:K", "E20:E"])

    updates = [] ## Stores changes for batch update (Less API calls)

    ## Separate data into different variables
    quotaSrikes = data[0] if data[0] else []
    hasInactivityNotice = data[1] if data[1] else []
    hasCompletedQuota = data[2] if data[2] else []
    joinDate = data[3] if data[3] else []
    weeklyEvents = data[4] if data[4] else []

    sevenDaysAgo = datetime.today() - timedelta(days=7)

    for i, (strikes, inactivity, quotaPassed, date, events) in enumerate(zip(quotaSrikes, hasInactivityNotice, hasCompletedQuota, joinDate, weeklyEvents), start=20):
        ## Handle for missing cells + flatlists
        strikes = strikes[0] if strikes else "0"
        inactivity = inactivity[0] if inactivity else "FALSE"
        quotaPassed = quotaPassed[0] if quotaPassed else "FALSE"
        date = str(date[0]) if date else str(datetime.today)
        events = events[0] if events else "0"

        ## If there data missing, skip current iteration
        if not strikes or not inactivity or not date:
            continue

        joinDateObj = datetime.strptime(date, "%Y-%m-%d") ## Convert join date cell into datetime object to compare it against seven days ago

        ## Logic for applying strikes
        if joinDateObj < sevenDaysAgo and inactivity == "FALSE" and quotaPassed == "FALSE":
            newStrike = int(strikes[0]) + 1
            updates.append({
                "range": f"G{i}",
                "values": [[newStrike]]
            })

        ## Reset weekly events to 0
        if events != 0:
            updates.append({
                "range": f"E{i}",
                "values": [[0]]
            })

    if updates:
        trooperSheet.batch_update(updates)
        await interaction.response.send_message(content=f"{interaction.user.mention} Quota has been checked, weekly events reset.")

client.run(credentials.botKey)