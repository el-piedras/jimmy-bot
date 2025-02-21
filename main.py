import discord
from discord.ext import commands
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
    robloxUser = username.nick or username.global_name or username.name
    userExists = trooperSheet.find(robloxUser, in_column=2)

    ## If user is already in DB, send response and cancel
    if userExists:
        await interaction.response.send_message(ephemeral=True, content=f"{interaction.user.mention} User {username.name} is already on the database.")
        return

    ## Data to insert for new members
    memberDefaultData = [robloxUser, "Recruit", 0, 0, 0, 0, "FALSE", 0, None, str(username.joined_at.date())]

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
        trooperSheet.append_row(memberDefaultData, value_input_option="USER_ENTERED")
        i + 1 ## Must accound index for the newly added row

    ## Generates and sends confirmation response
    newEmbed = discord.Embed(title="Added user", color=discord.Color.orange())
    newEmbed.add_field(name="Username", value=robloxUser, inline=True)
    newEmbed.add_field(name="Join date", value=username.joined_at.date(), inline=True)
    newEmbed.add_field(name="Row in Database", value=i, inline=True)
    newEmbed.set_footer(text="212th Attack Battalion Tracker")
    await interaction.response.send_message(embed=newEmbed)


@client.tree.command(name="fetch-data", description="Gets the specified user's join date, events attended and strikes", guild=GUILD_ID)
async def GetUserInfo(interaction: discord.Interaction, user: discord.Member):

    ## Checks if caller has permission
    userToCheck = GetInteractionCaller(interaction)

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

client.run(credentials.botKey)