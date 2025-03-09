import discord
from discord import app_commands
from discord.ext import commands
from config import GUILD_ID, DEFAULT_WORKSHEET
from sheets import sheet
from utils import CheckPermission, CompanyAutocomplete

class RemoveUserCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="remove-user",
        description="Removes the user from the database",
    )
    @app_commands.guilds(GUILD_ID)
    @app_commands.autocomplete(company=CompanyAutocomplete)
    @CheckPermission(3)
    async def RemoveUser(self, interaction: discord.Interaction, user: discord.Member, company: str = DEFAULT_WORKSHEET):

        workingSheet = sheet.worksheet(company)  # Opens selected worksheet

        userToRemove = user.nick or user.global_name or user.name   # Gets first available username
        usernameCell = workingSheet.find(userToRemove)  # Gets cell matching username

        # Cancel operation if no cell matching username was found
        if not usernameCell:
            await interaction.response.send_message(f"{interaction.user.mention} User not found in database.")
            return
        
        # If the username is in the LAST ROW in the table, delete the row
        if usernameCell.row == workingSheet.row_count:
            workingSheet.delete_rows(usernameCell.row)

        # Otherwise, replaces the values with the standard
        else:
            workingSheet.update(
                range_name=f"B{usernameCell.row}:K{usernameCell.row}",
                values=[["","","0","0","0","0","FALSE","0",f"=ARRAYFORMULA(IF(AND(E{usernameCell.row}>=3), TRUE, FALSE))",""]],
                value_input_option="USER_ENTERED"
            )

        await interaction.response.send_message(content=f"{interaction.user.mention} User has been successfully removed from the database.")    # Send response

async def setup(bot: commands.Bot):
    await bot.add_cog(RemoveUserCommand(bot))
    print("Loaded RemoveUserCommand cog.")