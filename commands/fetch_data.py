import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID, DEFAULT_WORKSHEET
from sheets import sheet
from utils import CheckPermission

class FetchData(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="fetch-data",
        description="Gets the specified user's join date, events attended and strikes",
    )
    @app_commands.guilds(GUILD_ID)
    @CheckPermission(1)
    async def GetUserInfo(self, interaction: discord.Interaction, user: discord.Member, company: str = DEFAULT_WORKSHEET):

        workingSheet = sheet.worksheet(company)  # Opens selected worksheet

        ## Checks if user is in database
        userToFetch = user.nick or user.global_name or user.name
        usernameCell = workingSheet.find(userToFetch)

        ## Cancel operation if NOT found
        if not usernameCell:
            await interaction.response.send_message(f"{interaction.user.mention} User was not found in the database.", ephemeral=True)
            return

        ## Otherwise, get the values from the row
        rowList = workingSheet.get(f"B{usernameCell.row}:K{usernameCell.row}")
        flatList = [
            "Yes" if item == "TRUE" else "No" if item == "FALSE" else item for item in rowList[0]
        ]

        ## Generate response...
        newEmbed = discord.Embed(title=f"Database data for {userToFetch}", color=discord.Color.orange())
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
        newEmbed.add_field(name="Row in DB", value=usernameCell.row)
        newEmbed.set_footer(text="212th Attack Battalion Tracker")
        await interaction.response.send_message(embed=newEmbed, delete_after=60)

async def setup(bot: commands.Bot):
    await bot.add_cog(FetchData(bot))
    print("Loaded FetchData cog.")