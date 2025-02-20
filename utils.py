import discord

## Dictionary with role IDs and their clearance level
CLEARANCE_LEVELS = {
    "epic role": 3, ## HICOM
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