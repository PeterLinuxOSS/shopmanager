
import nextcord
import pymongo
from nextcord.ext import commands
from nextcord.ext.commands import Bot
from termcolor import cprint

import config
from cogs.order import products
from cogs.subcategory import subcategory
from cogs.ticket import Start, ticketcs
from utils import db, sview, timestamp


class headcategory(nextcord.ui.Select):
    def __init__(self, bot ,selectOption):
        self.bot :Bot = bot 
        
                  
        if 2<= len(selectOption):
            max = 2
        else:
            max = 1           

            
        super().__init__(placeholder="Select:", min_values=1, max_values=max, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.send(f"{config.EMOJI_WAIT}Please wait, Creating your private channel{config.EMOJI_WAIT}",ephemeral=True) 
        guild = interaction.guild
        member = interaction.user
        print(self.values[0])
        ticketscount = await db.ticketsdb.count_documents({"userid":member.id,"guildid":guild.id})
        if ticketscount <= 3:
            events = await db.headcategorysdb.find_one({"guildid":interaction.guild_id, "headcategory":self.values[0]})
            print(events)
            if  events is not None and "run" in events :
                labe = events
                other = nextcord.utils.get(guild.categories, id=labe["categoryid"])
                
                overwrites = {guild.default_role: nextcord.PermissionOverwrite(read_messages=False)}
                try:
                    channel  = await guild.create_text_channel(name=f'📂・c-{member.name}' ,category=other,overwrites=overwrites)
                except nextcord.HTTPException:
                    await interaction.edit_original_message(content='In specific category is more than 50 tickets, please contact admin of server to delete some tickets.')
                else:
                    await channel.edit(sync_permissions=True)
                    db.ticketsdb.insert_one({"username": member.name, "userid": member.id,"guildid": guild.id, "channelid": channel.id, "date": timestamp,"category":self.values[0]})
                    
                    await channel.set_permissions(member, add_reactions=True, read_messages=True, view_channel=True, send_messages=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True, use_external_emojis=True, use_slash_commands=True)
                    
                    await interaction.edit_original_message(content=f'{member.mention} your private channel is here: {channel.mention}')
                    selectOption = []
                
                
                    styles = await db.embedstylesdb.find_one({"guildid":guild.id,"type":"submenu","headcategory":self.values[0]})
                    if "subcategory" in labe["run"]:
                                
                                subCategories = db.subcategoriesdb.find({"guildid":guild.id, "headcategory":self.values[0]})
                                print(styles)
                                
                                if  "type" in styles:
                                    stylesdb =styles
                                    if "description" in stylesdb:
                                        embedvalue = f"{stylesdb['description']}\n\n"
                                    else:
                                        embedvalue = ""
                                    numbers = 0    
                                    
                                    
                                    async for  value_value in subCategories:
                                        value_id = value_value["subcategory"]
                                        print(value_id) 
                                        
                                        numbers = numbers + 1
                                        if value_value  and "run" in value_value  :
                                            if "emoji" in value_value:

                                                if "description" in value_value and not "0" == value_value["description"]:
                                                    selectOption.append(nextcord.SelectOption(label=value_value["label"], description=value_value["description"],emoji=value_value["emoji"], value=value_id))
                                                    
                                                else:
                                                    selectOption.append(nextcord.SelectOption(label=value_value["label"],emoji=value_value["emoji"], value=value_id))
                                                embedvalue = embedvalue + f"{value_value['emoji']}・{value_value['label']}\n\n"
                                            else:
                                                if "description" in value_value and not "0" == value_value["description"]:
                                                    selectOption.append(nextcord.SelectOption(label=value_value["label"], description=value_value["description"], value=value_id))
                                                else:
                                                    selectOption.append(nextcord.SelectOption(label=value_value["label"], value=value_id))
                                        else:
                                            await interaction.send(f"you dont have setup subcategory or events! `/setup > Setup-Head-category >  Category {self.values[0]} > subCategory > {value_value['subcategory']} > Setup / Events`", ephemeral=True) 
                                            await channel.send(f"you dont have setup subcategory or events! `/setup > Setup-Head-category >  Category {self.values[0]} > subCategory > {value_value['subcategory']} > Setup / Events` ")
                                            break
                                            
                                    color = stylesdb["color"]
                                    color = int(hex(color), 0)         
                                    embed=nextcord.Embed(title=stylesdb["title"], description=embedvalue,color=color)
                                    
                                    if "image" in stylesdb:
                                        embed.set_image(url=stylesdb["image"])
                                    if "icon" in stylesdb:
                                        embed.set_thumbnail(url=stylesdb["icon"])
                                    if "footer-text" in stylesdb and "footer-icon" in stylesdb:
                                        embed.set_footer(text=stylesdb["footer-text"], icon_url=stylesdb["footer-icon"])
                                    elif "footer-text" in stylesdb :
                                        embed.set_footer(text=stylesdb["footer-text"])
                                    
                                    await channel.send(embed=embed, view=sview(self.bot,subcategory,interaction.user,None,selectOption))
                                else:
                                    await interaction.send("U dont have setup subcategory style", ephemeral=True)
                                    await channel.send("U dont have setup subcategory style")
                                


                        
                    elif labe["run"] == "products":
                        
                        x = db.productsdb.find({"guildid":interaction.guild_id, "headcategory":self.values[0],"enabled":True})
                        productsdbs = await x.to_list(length=None)
                        
                            
                        if len(productsdbs) != 0:
                            
                            
                            selectOption = []
                            numbers = 0
                            print(self.values[0])
                            stylesdb = await db.embedstylesdb.find_one({"guildid":interaction.guild_id, "type":"productsmenu","headcategory":self.values[0]})
                            if stylesdb :

                                
                                if "description" in stylesdb:
                                    embedvalue = f"{stylesdb['description']}\n\n"
                                else:
                                    embedvalue = ""

                                for  value_value in productsdbs:
                                        productdb = value_value
                                        value_id = str(value_value["_id"])
                                        print(value_id)
                                        numbers = numbers + 1
                                        
                                        emoji =value_value["emoji"]


                                        if 'fixed_price' in value_value and value_value['fixed_price']:    
                                            labeandprice = f"{value_value['label']} = {value_value['fixed_price']}€"
                                        else:
                                            labeandprice = f"{value_value['label']}"
                                        print(labeandprice)
                                        if  emoji:
                                            
                                            if "description" in value_value and not "0" == value_value["description"]:
                                                selectOption.append(nextcord.SelectOption(label=value_value['label'], description=value_value["description"],emoji=emoji, value=f"{value_id}"))
                                                
                                            else:
                                                selectOption.append(nextcord.SelectOption(label=value_value['label'],emoji=emoji, value=f"{value_id}"))
                                            embedvalue = embedvalue + f"{emoji}・{labeandprice}\n\n"
                                        else:
                                            if "description" in value_value and not "0" == value_value["description"]:
                                                selectOption.append(nextcord.SelectOption(label=value_value['label'], description=value_value["description"], value=f"{value_id}"))
                                            else:
                                                selectOption.append(nextcord.SelectOption(label=value_value['label'], value=f"{value_id}"))
                                if numbers != 1:


                                
                                    color = stylesdb["color"]
                                    color = int(hex(color), 0)
                                    embed=nextcord.Embed(title=stylesdb["title"], description=embedvalue,color=color)
                                            
                                    if "image" in stylesdb:
                                        embed.set_image(url=stylesdb["image"])
                                    if "icon" in stylesdb:
                                        embed.set_thumbnail(url=stylesdb["icon"])
                                    if "footer-text" in stylesdb:
                                        embed.set_footer(text=stylesdb["footer-text"])
                                    
                                    
                                    await channel.send(embed=embed , view=sview(self.bot,products,interaction.user,None,selectOption))
                                else:
                                    
                                    await channel.send("There is not any product so skipping menu",view=Start(self.bot ,productdb))
                                    
                                    
                                
                            else:
                                await channel.send("This server dont have setup product style!")
                        else:
                            await channel.send("This server dont have any products in this subcategory!")
                        
                    elif labe["run"] == "ticket":
                        await ticketcs.ticket(self=self,headcategorydb=labe,channel=channel) 
        else:
            await interaction.edit_original_message(content="You cant create more than 3 tickets!")   
  

                
                              
                

class headcategorycs(commands.Cog):
    
    

    def __init__(self, bot: Bot) -> None:
        self.bot = bot 
        
    
    
    async def refreshlables(self,guildid):
        guildsettin = await db.guildsdb.find_one({"guildid":guildid})
        if guildsettin is not None:
        
            stylesdb =await db.embedstylesdb.find_one({"guildid":guildid, "type":"headmenu"})
            if stylesdb :
                
                
                if "channelid" in stylesdb and "msgid" in stylesdb:
                    
                    channel = self.bot.get_channel(stylesdb["channelid"])

                    if channel :
                        
                        msg= await channel.fetch_message(stylesdb["msgid"])
                        
                        if msg and msg.author.id == self.bot.user.id: 
                            menu = db.headcategorysdb.find({"guildid":guildid}).sort("headcategory",pymongo.ASCENDING)
                            if menu is not None:
                                
                                selectOption = []
                                numbers = 0
                                
                                if "description" in stylesdb:
                                    description = f"{stylesdb['description']}\n\n"
                                else:
                                    description = ""
                                async for value_value in menu:
                                    
                                    
                                    
                                    print(value_value["headcategory"])
                                    value_id = str(value_value["headcategory"])
                                    print(value_id)
                                    value = True 
                                    if value:
                                        numbers = numbers + 1
                                        if "emoji" in value_value:

                                            if "description" in value_value and not "0" == value_value["description"]:
                                                selectOption.append(nextcord.SelectOption(label=value_value["label"], description=value_value["description"],emoji=value_value["emoji"], value=value_id))
                                                
                                            else:
                                                selectOption.append(nextcord.SelectOption(label=value_value["label"],emoji=value_value["emoji"], value=value_id))
                                            description = description + f"{value_value['emoji']}・{value_value['label']}\n\n"
                                        else:
                                            if "description" in value_value and not "0" == value_value["description"]:
                                                selectOption.append(nextcord.SelectOption(label=value_value["label"], description=value_value["description"], value=value_id))
                                            else:
                                                selectOption.append(nextcord.SelectOption(label=value_value["label"], value=value_id))

                                    color = stylesdb["color"]
                                    color = int(hex(color), 0)
                                    
                                    
                                    embed=nextcord.Embed(title=stylesdb["title"], description=description,color=color)

                                    
                                    if "image" in stylesdb:
                                        embed.set_image(url=stylesdb["image"])
                                    if "icon" in stylesdb:
                                        embed.set_thumbnail(url=stylesdb["icon"])
                                    if "footer-text" in stylesdb and "footer-icon" in stylesdb:
                                        embed.set_footer(text=stylesdb["footer-text"], icon_url=stylesdb["footer-icon"])
                                    elif "footer-text" in stylesdb:
                                        embed.set_footer(text=stylesdb["footer-text"])

                                    

                                
                                
                                


                

                                await msg.edit(content=None,embed=embed, view=sview(self.bot,headcategory,None,None,selectOption))
                                cprint(f"Refreshed for {msg.guild.name}","green")
                            else:
                                await msg.edit(content="Use `/setup > Setup-Head-Category`  to setup category/s",embed=None, view=None)
                        else:
                            menu = db.headcategorysdb.find({"guildid":guildid}).sort("headcategory",pymongo.ASCENDING)
                            if menu is not None:
                                
                                selectOption = []
                                numbers = 0
                                
                                if "description" in stylesdb:
                                    description = f"{stylesdb['description']}\n\n"
                                else:
                                    description = ""
                                async for value_value in menu:
                                    
                                    
                                    
                                    print(value_value["headcategory"])
                                    value_id = str(value_value["headcategory"])
                                    print(value_id)
                                    value = True 
                                    if value:
                                        numbers = numbers + 1
                                        if "emoji" in value_value:

                                            if "description" in value_value and not "0" == value_value["description"]:
                                                selectOption.append(nextcord.SelectOption(label=value_value["label"], description=value_value["description"],emoji=value_value["emoji"], value=value_id))
                                                
                                            else:
                                                selectOption.append(nextcord.SelectOption(label=value_value["label"],emoji=value_value["emoji"], value=value_id))
                                            description = description + f"{value_value['emoji']}・{value_value['label']}\n\n"
                                        else:
                                            if "description" in value_value and not "0" == value_value["description"]:
                                                selectOption.append(nextcord.SelectOption(label=value_value["label"], description=value_value["description"], value=value_id))
                                            else:
                                                selectOption.append(nextcord.SelectOption(label=value_value["label"], value=value_id))

                                    color = stylesdb["color"]
                                    color = int(hex(color), 0)
                                    
                                    
                                    embed=nextcord.Embed(title=stylesdb["title"], description=description,color=color)

                                    
                                    if "image" in stylesdb:
                                        embed.set_image(url=stylesdb["image"])
                                    if "icon" in stylesdb:
                                        embed.set_thumbnail(url=stylesdb["icon"])
                                    if "footer-text" in stylesdb and "footer-icon" in stylesdb:
                                        embed.set_footer(text=stylesdb["footer-text"], icon_url=stylesdb["footer-icon"])
                                    elif "footer-text" in stylesdb:
                                        embed.set_footer(text=stylesdb["footer-text"])

                                    

                                
                                
                                


                

                                msg = await channel.send(embed=embed, view=sview(self.bot,headcategory,None,None,selectOption))
                                cprint(f"Refreshed for {channel.guild.name}","green")
                            else:
                                msg = await channel.send(content="Use `/setup > Setup-Head-Category`  to setup category/s")
                            await db.embedstylesdb.update_one({"_id":stylesdb["_id"]},{'$set': {'msgid': msg.id}})

    

def setup(bot: Bot) -> None:
    bot.add_cog(headcategorycs(bot))