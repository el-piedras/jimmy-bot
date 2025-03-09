import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID, DEFAULT_WORKSHEET
from sheets import sheet
from utils import CheckPermission, CompanyAutocomplete


class AddUserClass(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
            name="add-user",
            description="Adds user to the Activity Tracker",
        )
    @app_commands.guilds(GUILD_ID)
    @app_commands.autocomplete(company=CompanyAutocomplete)
    @CheckPermission(3)
    async def AddUser(self, interaction: discord.Interaction, username: discord.Member, company: str = DEFAULT_WORKSHEET):

        workingSheet = sheet.worksheet(company)  # Opens the selected worksheet

        userToAdd = username.nick or username.global_name or username.name  # Checks if username exists in database
        usernameCell = workingSheet.find(userToAdd, in_column=2)    # Gets cell from matching username

        ## If user is already in DB, send response and cancel
        if usernameCell:
            await interaction.response.send_message(ephemeral=True, content=f"{interaction.user.mention} User {username.name} is already on the database.")
            return
         
        foundEmpty = False  # Flag to check if gaps exist
    
        trooperUsernameValue = workingSheet.get_values("B19:B") # Gets usernames from the database

        trooperUsernameValue = [value[0] if value else "" for value in trooperUsernameValue]    # Flattens the list and replaces null values with an empty string

        ## If gap is found, populate it first...
        for i, value in enumerate(trooperUsernameValue, start=20):

            ## Data to insert for new members
            memberDefaultData = [
                userToAdd,
                "Recruit",
                0,
                0,
                0,
                0,
                "FALSE",
                0, 
                f"=ARRAYFORMULA(IF(AND(E{i}>=3), TRUE, FALSE))",
                str(username.joined_at.date()),
            ]

            ## If an empty cell was found, then flip the gap flag and populate it first
            if value == "":
                workingSheet.update(range_name=f"B{i}:K{i}", values=[memberDefaultData], value_input_option="USER_ENTERED")
                foundEmpty = True
                break

        # If no gap is found, append a new row and populate it
        if not foundEmpty:
            i + 1 ## Must account index for the newly added row
            workingSheet.append_row(memberDefaultData, value_input_option="USER_ENTERED")

        ## Generates and sends confirmation response
        newEmbed = discord.Embed(title="Added user", color=discord.Color.orange())
        newEmbed.add_field(name="Username", value=userToAdd, inline=True)
        newEmbed.add_field(name="Join date", value=username.joined_at.date(), inline=True)
        newEmbed.add_field(name="Row in Database", value=i, inline=True)
        newEmbed.set_footer(text="212th Attack Battalion Tracker")
        await interaction.response.send_message(embed=newEmbed)

async def setup(bot: commands.Bot):
    await bot.add_cog(AddUserClass(bot))
    print("AddUserClass cog loaded.")