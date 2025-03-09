import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID, DEFAULT_WORKSHEET
from sheets import sheet
from datetime import timedelta, datetime
from utils import CheckPermission, CompanyAutocomplete

class QuotaCheck(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("QuotaCheck cog initialized")

    @app_commands.command(
        name="quota-check",
        description="Checks if anyone in the database hasn't completed their quota and applies strike if necessary.",
    )
    @app_commands.guilds(GUILD_ID)
    @app_commands.autocomplete(company=CompanyAutocomplete)  # Correct usage of autocomplete
    @CheckPermission(4)
    async def CheckQuota(self, interaction: discord.Interaction, company: str = DEFAULT_WORKSHEET):
        workingSheet = sheet.worksheet(company)  # Opens selected worksheet

        data = workingSheet.batch_get(["G20:G", "H20:H", "J20:J", "K20:K", "E20:E"])    # Gets the relevant data

        updates = [] ## Stores changes for batch update (Less API calls)

        ## Separate data into different variables
        quotaSrikes = data[0] if data[0] else []
        hasInactivityNotice = data[1] if data[1] else []
        hasCompletedQuota = data[2] if data[2] else []
        joinDate = data[3] if data[3] else []
        weeklyEvents = data[4] if data[4] else []
        sevenDaysAgo = datetime.today() - timedelta(days=7)

        # Decomposes the list of lists into a list, accounting for starting row
        for i, (strikes, inactivity, quotaPassed, date, events) in enumerate(zip(quotaSrikes, hasInactivityNotice, hasCompletedQuota, joinDate, weeklyEvents), start=20):

            ## Decomposes the lists into raw values, handling exceptions
            strikes = strikes[0] if strikes else "0"
            inactivity = inactivity[0] if inactivity else "FALSE"
            quotaPassed = quotaPassed[0] if quotaPassed else "FALSE"
            date = str(date[0]) if date else str(datetime.today().date())
            events = events[0] if events else "0"

            ## If there data missing, skip current iteration
            if not strikes or not inactivity or not date:
                continue
            
            joinDateObj = datetime.strptime(date, "%Y-%m-%d") ## Convert join date cell into datetime object to compare it against seven days ago

            ## Logic for applying strikes
            if joinDateObj < sevenDaysAgo and inactivity == "FALSE" and quotaPassed == "FALSE": # If user joined more than a week ago, doesn't have IN AND hasn't passed quota...
                newStrike = int(strikes[0]) + 1 # Adds a strike
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
        
        # If there are any changes, update them
        if updates:
            workingSheet.batch_update(updates, value_input_option="USER_ENTERED")
            await interaction.response.send_message(content=f"{interaction.user.mention} Quota has been checked, strikes applied, weekly events reset.")
        else:
            await interaction.response.send_message(content=f"{interaction.user.mention} Quota has been checked, no strikes applied, weekly events reset.") # I don't think this can ever happen, but just in case

async def setup(bot: commands.Bot):
    await bot.add_cog(QuotaCheck(bot))
    print("Loaded QuotaCheck cog")