import nextcord
from nextcord import Interaction
from nextcord.ext import commands
from nextcord.ext.commands import Bot

from cogs.helpers import helpers
from cogs.setup import presetup
from utils import embeds, sview


class commands(commands.Cog):
    
    

    def __init__(self, bot: Bot) -> None:
        self.bot = bot 
        
    @nextcord.slash_command(name="setup",description="setup ticket channel",)
    async def setup_command(self,interaction: Interaction, ):
        await interaction.send(content = embeds["1-Setup"]["content"], view=sview(self.bot,presetup, interaction.user, 120))
        
    @nextcord.slash_command(name="delete",description="delete ticket channel")
    async def delete_command(self,interaction: Interaction,):  
            await interaction.response.defer()
            await helpers.close_ticket(self,interaction)
            
            
    
        
    
    

def setup(bot: Bot) -> None:
    bot.add_cog(commands(bot))