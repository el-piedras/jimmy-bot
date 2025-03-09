import discord
import functools
from global_vars import workSheetNames
from discord import app_commands

## Dictionary with role IDs and their clearance level
CLEARANCE_LEVELS = {
    "HICOM": 4, ## HICOM
    "epic role": 3, ## SENIOR
    "less epic role": 2, ## OFFICER
    "trooper": 1  ## TROOPER
}

## Returns true if the highest clearance level found in the user is equal or higher to the required clearance level
def HasClearance(requiredClearance: int, interactionUser: discord.Member) -> bool:
    maxClearance = 0
    for role in interactionUser.roles:
        if role.name in CLEARANCE_LEVELS:
            maxClearance = max(maxClearance, CLEARANCE_LEVELS[role.name])

    if maxClearance >= requiredClearance:
        return True
    else:
        return False

## Prevents bot from using "User" instead of "Member" class    
async def GetInteractionCaller(interaction: discord.Interaction):
    caller = interaction.guild.get_member(interaction.user.id)
    if not caller:
        caller = await interaction.guild.fetch_member(interaction.user.id)
    elif not caller:
        return interaction.user
    return caller

async def CompanyAutocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=c, value=c)
        for c in workSheetNames if current.lower() in c.lower()
    ][:25]  # Limit to 25 choices

def CheckPermission(level: int):
    def Decorator(func):
        @functools.wraps(func)
        async def Wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            # Get the user who called the command
            print(f"Wrapper received interaction: {interaction}")
            user = await GetInteractionCaller(interaction)
            
            # Check if the user has the necessary clearance (permission)
            if not HasClearance(level, user):
                # Send an error message if the user doesn't have permission
                await interaction.response.send_message(ephemeral=True, content=f"{interaction.user.mention} You don't have permission to run this command.")
                return
            
            # If the user has permission, run the original function (command)
            return await func(self, interaction, *args, **kwargs)
        return Wrapper
    return Decorator