from nextcord.ext import commands
from nextcord.ext.commands import Bot

# (nothing needed from utils)

                
                              
                

class ui(commands.Cog):
    
    

    def __init__(self, bot: Bot) -> None:
        self.bot = bot 
        
        
    pass
        
    
    

def setup(bot: Bot) -> None:
    bot.add_cog(ui(bot))