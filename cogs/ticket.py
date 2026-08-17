
import nextcord
from nextcord import Interaction, TextChannel
from nextcord.ext import commands
from nextcord.ext.commands import Bot

from cogs.order import order

# (nothing needed from utils)


class Start(nextcord.ui.View):
    def __init__(self, bot:Bot,productdb ):
        super().__init__()
        self.bot = bot 
        self.value = None
        self.productdb = productdb
        
    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @nextcord.ui.button(label="Confirm", style=nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        
        await order.product_skipper(self,interaction, self.productdb,None)
        self.stop()         
         
                
      
                

class ticketcs(commands.Cog):
    
    

    def __init__(self, bot: Bot) -> None:
        self.bot = bot 
        
        
    async def ticket(self,headcategorydb,channel:TextChannel, subcategorydb=None):
        embed=nextcord.Embed(color=0x00ff00)
        embed.set_thumbnail(url=channel.guild.icon.url)
        embed.add_field(name=channel.guild.name, value="Thanks for open ticket please describe reason of opening it and wait for staff to respond.", inline=False)
        if not subcategorydb:
            
            embed.add_field(name="HeadCategory", value=f"{headcategorydb['emoji']}・{headcategorydb['label']}", inline=False)
            
        else:
            
            embed.add_field(name="HeadCategory", value=f"{headcategorydb['emoji']}・{headcategorydb['label']}", inline=False)
            embed.add_field(name="SubCategory", value=f"{subcategorydb['emoji']}・{subcategorydb['label']}", inline=False)
        if type(channel) == Interaction:
            interaction: Interaction = channel
            await interaction.message.edit(embed=embed,view=None,content=None)   
        else:
            
            await channel.send(embed=embed)                 
        
    
    

def setup(bot: Bot) -> None:
    bot.add_cog(ticketcs(bot))