import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID, DEFAULT_WORKSHEET
from sheets import sheet
from utils import CheckPermission, CompanyAutocomplete

class AddEventClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # Save the bot instance

    @app_commands.command(
        name="add-event",
        description="Adds an Event Point to the specified user's weekly, current company, and total events attended cells",
    )
    @app_commands.autocomplete(company=CompanyAutocomplete)
    @app_commands.guilds(GUILD_ID)
    @CheckPermission(2)
    async def add_event_point(self, interaction: discord.Interaction, user: discord.Member, company: str = DEFAULT_WORKSHEET):
        workingSheet = sheet.worksheet(company)
        userToAddEP = user.nick or user.global_name or user.name
        usernameCell = workingSheet.find(query=userToAddEP, in_column=2)

        if not usernameCell:
            await interaction.response.send_message(f"User {userToAddEP} wasn't found in DB")
            return

        rowToUpdate = workingSheet.get(range_name=f"D{usernameCell.row}:F{usernameCell.row}")
        newValues = [[str(int(x) + 1) for x in sublist] for sublist in rowToUpdate]
        workingSheet.update(range_name=f"D{usernameCell.row}:F{usernameCell.row}", values=newValues, value_input_option="USER_ENTERED")

        await interaction.response.send_message(f"{interaction.user.mention} Added 1EP to {user.mention}.")

# Setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(AddEventClass(bot))  # Pass the bot to the cog setup
    print("AddEventClass cog loaded.")
