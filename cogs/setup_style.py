
import nextcord
from nextcord import Embed, Interaction
from nextcord.ext import commands
from nextcord.ext.commands import Bot

import config
from cogs.headcategory import headcategorycs
from cogs.helpers import helpers
from utils import db, sview


class setupstylesub(nextcord.ui.Select):
    def __init__(self,bot:Bot,hcategory):
        self.bot = bot
        self.hcategory = hcategory
        selectOption = [
            
            nextcord.SelectOption(label="change embed title", emoji="🗃️" ,value="7", ),
            nextcord.SelectOption(label="change embed description", emoji="🗃️" ,value="3", ),
            nextcord.SelectOption(label="change embed color", emoji="🗃️" ,value="2", ),
            nextcord.SelectOption(label="add/change footer text", emoji="🗃️" ,value="4", ),
            nextcord.SelectOption(label="add/change/remove footer icon", emoji="🗃️" ,value="8", ),
            nextcord.SelectOption(label="add/change/remove embed image", emoji="🗃️" ,value="5", ),
            nextcord.SelectOption(label="add/change/remove thumbnail icon", emoji="🗃️" ,value="6", ),
            nextcord.SelectOption(label="Go Back",emoji="🔙", value = "00",)
            
            
            
         
            
            
           

        ]
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
            value = self.values[0]
            hcategory =f"category{self.hcategory}"
            

        
            styledb = list(db.embedstylesdb.find({"guildid":interaction.guild.id, "type":"submenu","headcategory":hcategory}))
            if len(styledb) != 0:
                if int(value) == 2:
                    await interaction.send("Please send your specific color in HEX format **with #**")
                    color, msg = await helpers.waitforrespon(self,interaction.channel,interaction.user,"hex",200)
                    if color:
                        db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"submenu","headcategory":hcategory}, {"$set":{"color":color}})
                        await interaction.channel.send(content=f"Successfully updated color to {color}")
                elif int(value) == 3:
                    await interaction.send("Please send what u want to have in description")
                    msg = await helpers.waitforrespon(self,interaction.channel,interaction.user,"msg",300)
                    if msg:
                        db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"submenu","headcategory":hcategory}, {"$set":{"description":msg.content}})
                        
                        await interaction.send(content=f"Successfully updated description to {msg.content}")


                elif int(value) == 4:
                    await interaction.send("Please send what u want to have in footer text")
                    msg = await helpers.waitforrespon(self,interaction.channel,interaction.user,"msg",300)
                    if msg:
                        db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"submenu","headcategory":hcategory}, {"$set":{"footer-text":msg.content}})
                        
                        await interaction.send(content=f"Successfully updated footer-text to {msg.content}")
                elif int(value) == 5:
                    await interaction.send("Please send link for your image(if you want remove image just send `0` or `no`)")
                    text = await helpers.waitforrespon(self,interaction.channel,interaction.user,"msg",300)
                    if text:
                        
                        if 'https://' in text.content  or 'http://' in text.content:
                            db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"submenu","headcategory":hcategory}, {"$set":{"image":text.content}})
                            
                            await interaction.send(content=f"Successfully updated image to {text.content}")
                        elif text.content.startswith("0") or text.content.startswith("no"):
                            db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"submenu","headcategory":hcategory}, {"$unset":{"image":""}})
                            
                            await interaction.send(content="Successfully removed image.")
                        
                        else:
                            embed=Embed(title="ERROR | incorrect link", description="Cancelled the Operation!", color=0xff0000)
                            if interaction.guild is not None or interaction.guild.icon.url is not None:
                                embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                            await interaction.edit_original_message(embed=embed)
                elif int(value) == 6:
                    await interaction.send("Please send link for your thumbnail icon (if you want remove image just send `0` or `no`)")
                    text = await helpers.waitforrespon(self,interaction.channel,interaction.user,"msg",300)
                    if text:
                        
                        if 'https://' in text.content  or 'http://' in text.content:
                            db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"submenu","headcategory":hcategory}, {"$set":{"icon":text.content}})
                            
                            await interaction.send(content=f"Successfully updated thumbnail icon to {text.content}")
                        elif text.content.startswith("0") or text.content.startswith("no"):

                            db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"submenu","headcategory":hcategory}, {"$unset":{"icon":""}})
                            await interaction.send(content="Successfully removed thumbnail icon.")
                        
                        else:
                            embed=Embed(title="ERROR | incorrect link", description="Cancelled the Operation!", color=0xff0000)
                            if interaction.guild is not None or interaction.guild.icon.url is not None:
                                embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                            await interaction.edit_original_message(embed=embed)
                elif int(value) == 7:
                    await interaction.send("Please send what u want to have in title")
                    text = await helpers.waitforrespon(self,interaction.channel,interaction.user,"msg",300)
                    if text:
                        db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"submenu","headcategory":hcategory}, {"$set":{"title":text.content}})
                        await interaction.send(content=f"Successfully updated title to {text.content}")

                elif int(value) == 8:
                    await interaction.send("Please send link for your footer  icon (if you want remove image just send `0` or `no`)")
                    text = await helpers.waitforrespon(self,interaction.channel,interaction.user,"msg",300)
                    if text:
                        
                        if 'https://' in text.content  or 'http://' in text.content:
                            db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"submenu","headcategory":hcategory}, {"$set":{"footer-icon":text.content}})
                            
                            await interaction.send(content=f"Successfully updated footer icon to {text.content}")
                        elif text.content.startswith("0") or text.content.startswith("no"):
                            db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"submenu","headcategory":hcategory}, {"$unset":{"footer-icon":""}})
                            
                            await interaction.send(content="Successfully removed footer icon.")
                        
                        else:
                            embed=Embed(title="ERROR | incorrect link", description="Cancelled the Operation!", color=0xff0000)
                            if interaction.guild is not None or interaction.guild.icon.url is not None:
                                embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                            await interaction.edit_original_message(embed=embed)
                if value == "00":

                    
                    pass
                    
                    
            
                else :
                    
                    
                    
                    await style.setupstylesub_menu(self,interaction,hcategory)
                    await headcategorycs.refreshlables(self,interaction.guild_id)
                

                


            else:
                embed=Embed(title="Error", description="**First you must setup the `setup required`**", color=0xfffff0)
                await interaction.send(embed=embed, ephemeral=True)

            



      





class setupstyleproducts(nextcord.ui.Select):
    def __init__(self,bot:Bot,hcategory,scategory=None):
        self.bot = bot 
        selectOption = [
            
            nextcord.SelectOption(label="change embed title", emoji="🗃️" ,value="7", ),
            nextcord.SelectOption(label="change embed description", emoji="🗃️" ,value="3", ),
            nextcord.SelectOption(label="change embed color", emoji="🗃️" ,value="2", ),
            nextcord.SelectOption(label="add/change footer text", emoji="🗃️" ,value="4", ),
            nextcord.SelectOption(label="add/change/remove footer icon", emoji="🗃️" ,value="8", ),
            nextcord.SelectOption(label="add/change/remove embed image", emoji="🗃️" ,value="5", ),
            nextcord.SelectOption(label="add/change/remove thumbnail icon", emoji="🗃️" ,value="6", ),
            nextcord.SelectOption(label="Go Back",emoji="🔙", value = "00",)
            
 

        ]
        self.hcategory =hcategory
        self.scategory =scategory
        
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0]
         
        hcategory = self.hcategory
        
        scategory = self.scategory
        
        if int(value) == 1:
            
            embed=Embed(title="Title", description="description\n\n:emoji1:・Category name1\n\n:emoji2:・Category name2\n\n:emoji1:・Category name3\n\n:emoji1:・Category name3\n\n:emoji4:・Category name4\n\n:emoji5:・Category name5\n\n:emoji6:・Category name6\n\n:emoji7:・Category name7\n\n:emoji8:・Category name8\n", color=0xc70000)
            embed.set_thumbnail(url=config.IMAGE_SETUP_TUTORIAL)
            embed.set_footer(text="footer text")
            embed.set_image(url=config.IMAGE_STANDARD_BANNER)
            
            
            await headcategorycs.refreshlables(self,interaction.guild_id)
            await interaction.send(content="Successfully created!")
            

        else:
            print(hcategory, scategory)
            styledb = db.embedstylesdb.find_one({"guildid":interaction.guild.id, "type":"productsmenu","headcategory":hcategory,"subcategory":scategory})
            print(styledb)
            if styledb :
                if int(value) == 2:
                    await interaction.send("Please send your specific color in HEX format **with #**")
                    # The original was `hex:str ;msg = helpers.waitforrespon(...)`: a bare
                    # annotation that never assigned `hex` (so `if hex:` tested the builtin
                    # and was always true, and the builtin itself was written to the
                    # database), and the coroutine was never awaited. Matches the working
                    # pattern used everywhere else for the "hex" check.
                    color, msg = await helpers.waitforrespon(self,interaction.channel,interaction.user,"hex",180)
                    if color:
                        db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$set":{"color":color}})

                        await interaction.send(content=f"Successfully updated color to {color}")
                        
                elif int(value) == 3:
                    await interaction.send("Please send what u want to have in description")
                    try:
                        text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
                    except Exception:
                        embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                        if interaction.guild is not None or interaction.guild.icon.url is not None:
                            embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                            await interaction.edit_original_message(embed=embed)
                    else:
                        db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$set":{"description":text.content}})
                        
                        await interaction.send(content=f"Successfully updated description to {text.content}")


                elif int(value) == 4:
                    await interaction.send("Please send what u want to have in footer text")
                    try:
                        text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
                    except Exception:
                        embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                        if interaction.guild is not None or interaction.guild.icon.url is not None:
                            embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                            await interaction.edit_original_message(embed=embed)
                    else:
                        db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$set":{"footer-text":text.content}})
                        
                        await interaction.send(content=f"Successfully updated footer-text to {text.content}")
                elif int(value) == 5:
                    await interaction.send("Please send link for your image(if you want remove image just send `0` or `no`)")
                    try:
                        text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
                    except Exception:
                        embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                        if interaction.guild is not None or interaction.guild.icon.url is not None:
                            embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                            await interaction.edit_original_message(embed=embed)
                    else:
                        
                        if 'https://' in text.content  or 'http://' in text.content:
                            db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$set":{"image":text.content}})
                            
                            await interaction.send(content=f"Successfully updated image to {text.content}")
                        elif text.content.startswith("0") or text.content.startswith("no"):
                            db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$unset":{"image":""}})
                            
                            await interaction.send(content="Successfully removed image.")
                        
                        else:
                            embed=Embed(title="ERROR | incorrect link", description="Cancelled the Operation!", color=0xff0000)
                            if interaction.guild is not None or interaction.guild.icon.url is not None:
                                embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                            await interaction.edit_original_message(embed=embed)
                elif int(value) == 6:
                    await interaction.send("Please send link for your thumbnail icon (if you want remove image just send `0` or `no`)")
                    try:
                        text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
                    except Exception:
                        embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                        if interaction.guild is not None or interaction.guild.icon.url is not None:
                            embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                            await interaction.edit_original_message(embed=embed)
                    else:
                        
                        if 'https://' in text.content  or 'http://' in text.content:
                            db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$set":{"icon":text.content}})
                            
                            await interaction.send(content=f"Successfully updated thumbnail icon to {text.content}")
                        elif text.content.startswith("0") or text.content.startswith("no"):

                            db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$unset":{"icon":""}})
                            await interaction.send(content="Successfully removed thumbnail icon.")
                        
                        else:
                            embed=Embed(title="ERROR | incorrect link", description="Cancelled the Operation!", color=0xff0000)
                            if interaction.guild is not None or interaction.guild.icon.url is not None:
                                embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                            await interaction.edit_original_message(embed=embed)
                elif int(value) == 7:
                    await interaction.send("Please send what u want to have in title")
                    try:
                        text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
                    except Exception:
                        embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                        if interaction.guild is not None or interaction.guild.icon.url is not None:
                            embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                            await interaction.edit_original_message(embed=embed)
                    else:
                        db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$set":{"title":text.content}})
                        await interaction.send(content=f"Successfully updated title to {text.content}")

                elif int(value) == 8:
                    await interaction.send("Please send link for your footer  icon (if you want remove image just send `0` or `no`)")
                    try:
                        text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
                    except Exception:
                        embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                        if interaction.guild is not None or interaction.guild.icon.url is not None:
                            embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                            await interaction.edit_original_message(embed=embed)
                    else:
                        
                        if 'https://' in text.content  or 'http://' in text.content:
                            db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$set":{"footer-icon":text.content}})
                            
                            await interaction.send(content=f"Successfully updated footer icon to {text.content}")
                        elif text.content.startswith("0") or text.content.startswith("no"):
                            db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$unset":{"footer-icon":""}})
                            
                            await interaction.send(content="Successfully removed footer icon.")
                        
                        else:
                            embed=Embed(title="ERROR | incorrect link", description="Cancelled the Operation!", color=0xff0000)
                            if interaction.guild is not None or interaction.guild.icon.url is not None:
                                embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                            await interaction.edit_original_message(embed=embed)
                if value == "00":

                    
                    pass
                    
            
                else :
                    
                    
                    await style.setupstyleproducts_menu(self,interaction,hcategory,scategory)

                    await headcategorycs.refreshlables(self,interaction.guild_id)

                


            else:
                embed=Embed(title="Error", description="**First you must setup the `setup required`**", color=0xfffff0)
                await interaction.send(embed=embed, ephemeral=True)

            
  

                
                              
                

class style(commands.Cog):
    
    

    def __init__(self, bot: Bot) -> None:
        self.bot = bot 
        
    async def setupstyleproducts_menu(self,interaction: nextcord.Interaction, hcategory,scategory=None):
        embed=Embed(title="Products Ui", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
        embed.set_image(url=config.IMAGE_STYLE_TUTORIAL)
        
        await interaction.send(embed=embed, view=sview(self.bot,setupstyleproducts, interaction.user,120,f"category{hcategory}",f"subcategory{scategory}" if scategory else None ))    

    async def setupstylesub_menu(self,interaction:Interaction,hcategory,):
        embed=Embed(title="sub-Category Ui", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
        embed.set_image(url=config.IMAGE_STYLE_TUTORIAL)
        await interaction.send(embed=embed, view=sview(self.bot,setupstylesub,interaction.user,120,hcategory))   
    
    

def setup(bot: Bot) -> None:
    bot.add_cog(style(bot))