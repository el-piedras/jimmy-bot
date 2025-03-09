import discord
from discord.ext import commands
from sheets import sheet
import credentials
from config import GUILD_ID
from global_vars import workSheetNames
from commands.add_event import AddEventClass

class Client(commands.Bot):
    
    async def setup_hook(self):
        print("Loading extensions...")
        await self.load_extension("commands.add_event")
        await self.load_extension("commands.add_user")
        await self.load_extension("commands.fetch_data")
        await self.load_extension("commands.quota_check")
        await self.load_extension("commands.remove_user")
        print("Extensions loaded.")
        
    async def on_ready(self):
        global workSheetNames 

          # Fetch and store worksheet names
        try:
            workSheetNames.clear()  # Clear existing list to avoid duplication
            workSheetNames.extend([ws.title for ws in sheet.worksheets()])  # Store worksheet names
            print(f"Loaded worksheet names: {workSheetNames}")

        except Exception as e:
            print(f"Error loading worksheet names: {e}") 


        print(f'Logged in as {self.user}')
        try:
            guild = GUILD_ID
            print(f"Syncing commands to guild {guild.id}...")
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands to guild {guild.id}')
        except Exception as e:
            print(f'Commands failed to sync: {e}')

# Setup intents
intents = discord.Intents.default()
intents.message_content = True

# Create the bot instance
bot = Client(command_prefix=';', intents=intents)

# Ensure the bot instance is passed into the cog setup
async def setup():
    await bot.add_cog(AddEventClass(bot))  # Pass the bot to the cog setup
    print("AddEventClass cog loaded.")

bot.run(credentials.botKey)
