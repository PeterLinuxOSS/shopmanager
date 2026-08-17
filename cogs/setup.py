import asyncio
import datetime

import nextcord
from bson import ObjectId
from nextcord import Colour, Embed, Interaction, TextChannel, User
from nextcord.ext import commands
from nextcord.ext.commands import Bot
from nextcord.utils import get

import config
from cogs.headcategory import headcategorycs
from cogs.helpers import Confirm_clear, helpers
from cogs.setup_products import ProductVersion, productedit
from cogs.setup_style import style
from utils import can_dm_user, db, embeds, sview, timestamp


class setup_view(nextcord.ui.Select):
    def __init__(self,bot:Bot,userid):
        self.bot = bot 
        
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=userid)

    async def callback(self, interaction: nextcord.Interaction):
        hcategory = self.values[0]
        
        
        await setup_settings.headcategorysetup_menu(self,interaction,hcategory)

class selectsubcategory(nextcord.ui.Select):
    
    def __init__(self,bot:Bot,selectOption,hcategory,scategory,headkeys):
        self.bot = bot 
        self.hcategory= hcategory
        self.scategory =scategory
        self.headkeys =headkeys
        
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        hcategory =self.hcategory
        scategory =self.scategory 
        headkeys = self.headkeys
        db.subkeys = ObjectId(self.values[0])
        embed = nextcord.Embed(title="Product Version", description="**Select what you need in the `Selection` down Below!**", color=Colour.gold(), timestamp=timestamp,)
        await interaction.send(embed=embed,view=sview(self.bot,ProductVersion, interaction.user,120,hcategory,scategory,"keys",headkeys,db.subkeys))
        

class selectheadcategory(nextcord.ui.Select):
    def __init__(self,bot:Bot,selectOption,hcategory,scategory):
        self.bot = bot 
        self.hcategory= hcategory
        self.scategory =scategory
        
        
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        hcategory =self.hcategory
        scategory =self.scategory 
        headkeys = ObjectId(self.values[0])
        subkeyss = list(db.subkeys.find({"database":headkeys}))
        if len(subkeyss) != 0:
            selectOption = []
            count =0
            for subkey in subkeyss:
                count +=1
                selectOption.append(nextcord.SelectOption(label=f"**{count}.** {subkey['label']}", value=f'{subkey["_id"]}'))
                description = f"{count}. {subkey['label']}\n"
            embed = nextcord.Embed(title="Select Key/s HeadCategory", description=description, color=Colour.blurple(), timestamp=timestamp,)
            await interaction.send(embed=embed,view=sview(self.bot, selectsubcategory , interaction.user,120,selectOption,hcategory,scategory,headkeys))
        else:
            goods = list(db.goodsdb.find( { "type": { "$not": { "$regex": "^keys.*" } } } ))
            selectOption = []
            selectOption.append(nextcord.SelectOption(label="Keys", emoji="🟡" ,value="keys", ),)
            description = ""
            emojilist = ["🔴","🟠","🟡","🟢","🔵","🟣","🟤","⚫","⚪"]
            count =0 
            for good in goods:
                count +=1
                selectOption.append(nextcord.SelectOption(label=f"{count}. {good['label']}", value=f'{good["_id"]}', emoji=emojilist[(count-1)]))
                description = f"{emojilist[(count-1)]} {count}. {good['label']}\n"
            count +=1
            selectOption.append(nextcord.SelectOption(label=f"{count}. Manual delivery goods", value="manual", emoji=emojilist[(count-1)]))
            embed = nextcord.Embed(title="Error - You dont have any keys category", description="Please Select anything else", color=Colour.brand_red(), timestamp=timestamp ,)
            await interaction.send(embed=embed, view= sview(self.bot,SelectGoodsType, interaction.user, 120,selectOption,hcategory,scategory))




            
            


class SelectGoodsType(nextcord.ui.Select):
    def __init__(self,bot:Bot,selectOption,hcategory,scategory=None):
        self.bot = bot 
        
        self.hcategory= hcategory
        self.scategory =scategory
        super().__init__(placeholder="select goods type ...", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0]
        hcategory =self.hcategory
        scategory =self.scategory       
        if value == "manual":
            embed = nextcord.Embed(title="Product Version", description="**Select what you need in the `Selection` down Below!**", color=Colour.gold(), timestamp=timestamp,)
            await interaction.send(embed=embed,view=sview(self.bot,ProductVersion, interaction.user,120,hcategory,scategory,"manual"))
        else:
            if value == "keys":
                headkeys = list(db.goodsdb.find({"guilds":interaction.guild_id,"type":"keys"}))
                if len(headkeys) != 0:
                    selectOption = []
                    count =0
                    description = ""
                    for headkey in headkeys:
                        count +=1
                        selectOption.append(nextcord.SelectOption(label=f"{count}. {headkey['label']}", value=f'{headkey["_id"]}'))
                        description += f"**{count}.** {headkey['label']}\n"
                    embed = nextcord.Embed(title="Select Key/s HeadCategory", description=description, color=Colour.blurple(), timestamp=timestamp,)
                    await interaction.send(embed=embed,view=sview(self.bot, selectheadcategory , interaction.user,120,selectOption,hcategory,scategory))
                        
                        
                        
                else:
                    pass
                    # need error
            else:
                
                good = db.goodsdb.find_one({"guilds":interaction.guild_id,"_id":ObjectId(value)})
                if good["type"] == "commendbot":
                    embed = nextcord.Embed(title="Product Version", description="**Select what you need in the `Selection` down Below!**", color=Colour.gold(), timestamp=timestamp,)
                    await interaction.send(embed=embed,view=sview(self.bot,ProductVersion, interaction.user,120,hcategory,scategory,"commendbot"))
                    
                    
                elif good["type"] == "senpay":
                    pass
                    
                
                    
                elif good["type"] == "tf2keys":
                    embed = nextcord.Embed(title="Product Version", description="**Select what you need in the `Selection` down Below!**", color=Colour.gold(), timestamp=timestamp,)
                    await interaction.send(embed=embed,view=sview(self.bot,ProductVersion, interaction.user,120,hcategory,scategory,"tf2keys"))
                    
                elif good["type"] == "ranksmm":
                    embed = nextcord.Embed(title="Product Version", description="**Select what you need in the `Selection` down Below!**", color=Colour.gold(), timestamp=timestamp,)
                    await interaction.send(embed=embed,view=sview(self.bot,ProductVersion, interaction.user,120,hcategory,scategory,"ranksmm"))



class setupsubcategory2(nextcord.ui.Select):
    def __init__(self,bot:Bot,hcategory,scategory):
        self.bot = bot 
        selectOption = [
            nextcord.SelectOption(label="Setup", emoji="⚙️" ,value="1"),
            nextcord.SelectOption(label="Change", emoji="⚒️" ,value="2"),
            nextcord.SelectOption(label="Events", emoji="🎫" ,value="3"),
            
            nextcord.SelectOption(label="Products", emoji="🛒" ,value="4"),
            nextcord.SelectOption(label="Products Style", emoji="🎨" ,value="6"),
            nextcord.SelectOption(label="Cancel", emoji="🔴" ,value="5"),
            nextcord.SelectOption(label="Go Back",emoji="🔙", value = "00",),
            
 

        ]
        self.scategory =scategory
        self.hcategory=hcategory
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0]
        hcategory = self.hcategory
        scategory =self.scategory
        view = None
        
            
        print(value)
        if int(value) == 1:
            test_value = db.subcategoriesdb.find_one({"guildid":interaction.guild_id , "headcategory":f"category{hcategory}", "subcategory":f"subcategory{scategory}"})
            if test_value is None:

                embed=Embed(title="What name(title) do you wanna use?", description="Just send in the Chat category name", color=0x23929a)
                embed.set_image(url=config.IMAGE_PRODUCT_TUTORIAL)
                if interaction.guild is not None or interaction.guild.icon.url is not None:
                        embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                await interaction.message.edit(embed=embed,view=None)

                try:
                    text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
                except Exception:
                    embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                    if interaction.guild is not None or interaction.guild.icon.url is not None:
                        embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                    await interaction.send(embed=embed)
                else:
                    await text.delete()
                    category_name = text.content
                    embed=Embed(title="What description do you wanna use?", description="Just send in the Chat description **if you want category without a description just send `0` or `no` in this channel**", color=0x23929a)
                    embed.set_image(url=config.IMAGE_PRODUCT_TUTORIAL)
                    if interaction.guild is not None or interaction.guild.icon.url is not None:
                        embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                    await interaction.message.edit(embed=embed,view=None)
                    try:
                        text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
                    except Exception:
                        embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                        if interaction.guild is not None or interaction.guild.icon.url is not None:
                            embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                        await interaction.send(embed=embed)
                    else:
                        await text.delete()
                        if not "0" == text.content or not "no" == text.content:
                            category_description = text.content

                        embed=Embed(title="What emoji do you wanna use?", description="Just __**react**__ with your emoji(only server emojis or default emojis)", color=0x23929a)
                        embed.set_image(url=config.IMAGE_PRODUCT_TUTORIAL)
                        if interaction.guild is not None or interaction.guild.icon.url is not None:
                                embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                        msg = await interaction.message.edit(embed=embed,view=None)

                        try:
                            reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction,user: reaction.message.id == msg.id and user.id == interaction.user.id, timeout=180)
                        except Exception:
                            embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                            if interaction.guild is not None or interaction.guild.icon.url is not None:
                                embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                            await interaction.channel.send(embed=embed)
                        else:
                            
                            await reaction.remove(user)
                            
                            product_emoji = str(reaction)
                            testvalue = product_emoji.replace(">" , "").split(":")
                            if 2 in testvalue :

                                testvalue = int(testvalue[2])
                                
                                
                                emoji = self.bot.get_emoji(testvalue)
                                
                                if emoji is not None:
                                    if category_description is not None:
                                        db.subcategoriesdb.insert_one({"guildid":interaction.guild_id , "headcategory":f"category{hcategory}", "subcategory":f"subcategory{scategory}" ,"label":category_name, "emoji":product_emoji})
                                        
                                        
                                    else:
                                        db.subcategoriesdb.insert_one({"guildid":interaction.guild_id , "headcategory":f"category{hcategory}", "subcategory":f"subcategory{scategory}" ,"label":category_name, "emoji":product_emoji, "description":category_description})
                                        
                                    await headcategorycs.refreshlables(self,interaction.guild_id)
                                    await interaction.channel.send(f"**{config.EMOJI_YES}  Added the Category to the menu**",delete_after=30)
                                else:
                                    embed=Embed(title="ERROR | This emoji isnt on your server!", description="Cancelled the Operation!", color=0xff0000)
                                    if interaction.guild is not None or interaction.guild.icon.url is not None:
                                        embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                                    await interaction.channel.send(embed=embed,delete_after=30)
                            else:
                                emoji = testvalue[0]
                                if emoji:
                                    if category_description is not None:
                                        db.subcategoriesdb.insert_one({"guildid":interaction.guild_id , "headcategory":f"category{hcategory}", "subcategory":f"subcategory{scategory}" ,"label":category_name, "emoji":product_emoji})
                                        
                                        
                                    else:
                                        db.subcategoriesdb.insert_one({"guildid":interaction.guild_id , "headcategory":f"category{hcategory}", "subcategory":f"subcategory{scategory}" ,"label":category_name, "emoji":product_emoji, "description":category_description})
                                        
                                    await headcategorycs.refreshlables(self,interaction.guild_id)
                                    await interaction.channel.send(f"**{config.EMOJI_YES}  Added the Category to the menu**",delete_after=5)
                                else:
                                    embed=Embed(title="ERROR | This emoji isnt on your server!", description="Cancelled the Operation!", color=0xff0000)
                                    if interaction.guild is not None or interaction.guild.icon.url is not None:
                                        embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                                    await interaction.channel.send(embed=embed,delete_after=30)
            else:
                embed=Embed(title="ERROR | You cant setup again!", description="Cancelled the Operation!", color=0xff0000)
                if interaction.guild is not None or interaction.guild.icon.url is not None:
                    embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                await interaction.channel.send(embed=embed)
        elif int(value) == 2:
            await interaction.channel.send("Peter is too lazy to add this function so ll be available soon xd, if u want smth change pls contact the [STT_Esports] PeterLinuxOS#5964 (<@640961296665149440>) ")
                        
        elif int(value) == 3:
            event2 = db.subcategoriesdb.find_one({"guildid":interaction.guild_id , "headcategory":f"category{hcategory}", "subcategory":f"subcategory{scategory}"})
            if event2:
                embed=Embed(title="Events Setup", description="**Select what you need in the `Selection` down Below!**", color=0x23929a) # for subcategory
                view = sview(self.bot,selectevent, interaction.user, 120, hcategory, scategory)
                await interaction.message.edit(embed=embed, view=view)
            else:
                await interaction.channel.send("first setup subCategory") 

        elif int(value) == 4:
            

            event2 = db.subcategoriesdb.find_one({"guildid":interaction.guild_id , "headcategory":f"category{hcategory}", "subcategory":f"subcategory{scategory}"})
            if event2:
                if   "run" in event2:
                    view = "idk"
                    await setup_settings.productsmanager(self,interaction,hcategory,scategory)
                else:
                    await interaction.channel.send("You dont have setup events for subCategory")
            else:
                await interaction.channel.send("first setup subCategory") 
        elif int(value) == 6:
            await style.setupstyleproducts_menu(self,interaction,hcategory,scategory)
        if value == "00":

            await setup_settings.subcategorys_setup(self,interaction, hcategory)
        else :
            if view is None:
                await setup_settings.subcategory_menu(self,interaction, hcategory,scategory)
                return


class selectevent(nextcord.ui.Select):
    def __init__(self,bot:Bot,hcategory,scategory=None):
        self.bot = bot 
        selectOption = [
            
            nextcord.SelectOption(label="Show Products", emoji="💰" ,value="2", ),
            nextcord.SelectOption(label="Just create the ticket", emoji="🎫" ,value="3", ),
            

        ]
        if not scategory:
            selectOption.insert(0, nextcord.SelectOption(label="Show subCategories", emoji="🗂️" ,value="1", ),)
        self.hcategory = hcategory
        self.scategory =scategory
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0]
        hcategory = self.hcategory
        scategory = self.scategory
        
            
        if int(value) == 1:
            changeto = f"subcategory{hcategory}"
            embtry = db.embedstylesdb.find_one({"guildid":interaction.guild_id,"type":"submenu","headcategory":f"category{hcategory}"})
            if embtry is None:
                db.embedstylesdb.insert_one({"guildid":interaction.guild_id,"type":"submenu","headcategory":f"category{hcategory}",  "color":0xc70000,  "title":"title", "description":"description", })
        elif int(value) == 2:
            changeto = "products"
            embtry = db.embedstylesdb.find_one({"guildid":interaction.guild_id,"type":"productsmenu","headcategory":f"category{hcategory}","subcategory":f"subcategory{scategory}"})
            if embtry is None:
                db.embedstylesdb.insert_one({"guildid":interaction.guild_id,"type":"productsmenu","headcategory":f"category{hcategory}","subcategory":f"subcategory{scategory}",  "color":0xc70000,  "title":"title", "description":"description", })
            embtry2 = db.embedstylesdb.find_one({"guildid":interaction.guild_id,"type":"payments","headcategory":f"category{hcategory}","subcategory":f"subcategory{scategory}"})
            if not embtry2:
                db.embedstylesdb.insert_one({"guildid":interaction.guild_id,"type":"payments","headcategory":f"category{hcategory}","subcategory":f"subcategory{scategory}",  "color":0xc70000,  "title":"title pay", "description":"description", })
        elif int(value) == 3:
            changeto = "ticket"
        if not scategory:
            db.headcategorysdb.update_one({"guildid":interaction.guild_id, "headcategory":f"category{hcategory}"}, {"$set":{"run":changeto}})
        else:
            db.subcategoriesdb.update_one({"guildid":interaction.guild_id, "headcategory":f"category{hcategory}", "subcategory":f"subcategory{scategory}"}, {"$set":{"run":changeto}})
        await interaction.send(f"**{config.EMOJI_YES}  Successfuly changed option to {changeto} !**")
        await headcategorycs.refreshlables(self,interaction.guild_id)  
        if scategory :
            await setup_settings.subcategory_menu(self,interaction, hcategory,scategory)
            
                                                                      
       


class cateproducts(nextcord.ui.Select):
    def __init__(self,bot:Bot,selectOption,hcategory,scategory=None):
        self.bot = bot 
        
        self.hcategory= hcategory
        self.scategory =scategory
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0]
        hcategory =self.hcategory
        scategory =self.scategory
        view = None 
        if int(value) == 1:

            
            goods = list(db.goodsdb.find( { "type": { "$not": { "$regex": "^keys.*" } } } ))
            selectOption = []
            selectOption.append(nextcord.SelectOption(label="Keys", emoji="🟡" ,value="keys", ),)
            description = ""
            emojilist = ["🔴","🟠","🟡","🟢","🔵","🟣","🟤","⚫","⚪"]
            count =0 
            for good in goods:
                count +=1
                selectOption.append(nextcord.SelectOption(label=f"{count}. {good['label']}", value=f'{good["_id"]}', emoji=emojilist[(count-1)]))
                description = f"{emojilist[(count-1)]} {count}. {good['label']}\n"
            count +=1
            selectOption.append(nextcord.SelectOption(label=f"{count}. Manual delivery goods", value="manual", emoji=emojilist[(count-1)]))
            embed = nextcord.Embed(title="Goods type", description=description, color=Colour.yellow(), timestamp=timestamp,)
            await interaction.send(embed=embed, view=sview(self.bot,SelectGoodsType, interaction.user, 120,selectOption,hcategory,scategory))
            

        elif int(value) == 2:  

            
            spcategory = db.headcategorysdb.find_one({"guildid":interaction.guild_id,"headcategory":f"category{hcategory}"})
            if spcategory :
                if scategory is None :
                    products = db.productsdb.find({"guildid":interaction.guild_id, "headcategory": f"category{hcategory}"})        
                else: 
                    products = db.productsdb.find({"guildid":interaction.guild_id, "headcategory": f"category{hcategory}", "subcategory":f"subcategory{scategory}"})
                    
                    
                        
                            
                            
                            
                selectOption = []
                embedvalue = ""
                counter = 0 
                for value_value in products:
                    counter = counter + 1
                    value_id = str(value_value["_id"])
                    print(value_value["emoji"])
                    if "fixed_price" in value_value:
                            labeandprice = f"{value_value['label']} = {value_value['fixed_price']}€"
                    elif "type" in value_value and "ranksmm" in value_value["type"]:
                        labeandprice = f"{value_value['label']} starts on {value_value['ranks'][0]}€"
                            
                    else:
                            labeandprice = f"{value_value['label']} = {value_value['variable_price']}"
                    emoji = value_value["emoji"]
                    print(labeandprice)
                    if  emoji:
                        await interaction.channel.send(emoji)
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
                if counter != 0:
                    view = sview(self.bot,productcategoryedit, interaction.user,120, selectOption,hcategory,scategory)
                    embed=Embed(title="Select product!", description="**Selecect in, what product u want to make change** ", color=0x23929a)
                    await interaction.channel.send(embed=embed, view=view)

                else:
                    await interaction.send("You dont have any products in this sub/category")
        if value == "00":
            if scategory:
                await setup_settings.subcategory_menu(self,interaction,hcategory,scategory)
            else:
                await setup_settings.headcategorysetup_menu(self,interaction,hcategory)
        else :
            if view is None:
                await setup_settings.productsmanager(self,interaction,hcategory,scategory)
                

class productcategoryedit(nextcord.ui.Select):
    def __init__(self,bot:Bot,selectOption,hcategory,scategory=None):
        self.bot = bot 
        self.hcategory= hcategory
        self.scategory =scategory
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
            productid = self.values[0]
            hcategory = self.hcategory
            scategory  =self.scategory

            embed=Embed(title="Select what u want to edit", description="**Select what you need in the `Selection` down Below!**", color=0xfffff0)
            await interaction.send(embed=embed , view=sview(self.bot,productedit,interaction.user,120,productid,hcategory,scategory))
            
            

            



                   
            


class setupstylehead(nextcord.ui.Select):
    def __init__(self,bot:Bot,):
        self.bot  = bot 
        selectOption = [
            nextcord.SelectOption(label="setup required", emoji="⚙️" ,value="1", ),
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
        
        
        if int(value) == 1:
            if db.embedstylesdb.find_one({"guildid":interaction.guild_id, "type":"headmenu"}) is None:
                await interaction.send("Creating channel...")
                channel = await interaction.guild.create_text_channel(name="Change-name",overwrites = {interaction.guild.default_role: nextcord.PermissionOverwrite(read_messages=True, view_channel=True, send_messages=False)})
                embed=Embed(title="Title", description="description\n\n:emoji1:・Category name1\n\n:emoji2:・Category name2\n\n:emoji1:・Category name3\n\n:emoji1:・Category name3\n\n:emoji4:・Category name4\n\n:emoji5:・Category name5\n\n:emoji6:・Category name6\n\n:emoji7:・Category name7\n\n:emoji8:・Category name8\n", color=0xc70000)
                embed.set_thumbnail(url=config.IMAGE_SETUP_TUTORIAL)
                embed.set_footer(text="footer text")
                embed.set_image(url=config.IMAGE_STANDARD_BANNER)
                msg = await channel.send(embed=embed)
                

                db.embedstylesdb.insert_one({"guildid":interaction.guild_id,"type":"headmenu", "channelid":channel.id, "msgid":msg.id ,"color":0xc70000,  "title":"title", "description":"description"})
            
                await headcategorycs.refreshlables(self,self,interaction.guild_id)
                await interaction.edit_original_message(content="Successfully created channel and sent random message!")
            else:
                await interaction.send("you cant create again!")
            

        else:
            styledb = db.embedstylesdb.find({"guildid":interaction.guild.id, "type":"headmenu"})
            
            if   styledb is not None:
                if int(value) == 2:
                    await interaction.send("Please send your specific color in HEX format **with #**")
                    color , msg = await helpers.waitforrespon(self,interaction.channel,interaction.user,"hex",180)
                    if color:
                            db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$set":{"color":color}})
                            await msg.channel.send(content=f"Successfully updated color to {msg.content}")
                     
                elif int(value) == 3:
                    await interaction.send("Please send what u want to have in description")
                    msg = await helpers.waitforrespon(self,interaction.channel,interaction.user,"msg",180)
                    if msg:
                        
                        db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$set":{"description":msg.content}})
                        
                        await msg.channel.send(content=f"Successfully updated description to {msg.content}")


                elif int(value) == 4:
                    await interaction.send("Please send what u want to have in footer text")
                    msg = await helpers.waitforrespon(self,interaction.channel,interaction.user,"msg",180)
                    if msg:
                        db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$set":{"footer-text":msg.content}})
                        
                        await msg.channel.send(content=f"Successfully updated footer-text to {msg.content}")
                elif int(value) == 5:
                    await interaction.send("Please send link for your image(if you want remove image just send `0` or `no`)")
                    image ,msg = await helpers.waitforrespon(self,interaction.channel,interaction.user,"image_n",180)
                    if isinstance(image, str):
                            
                        
                            db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$set":{"image":image}})
                            
                            await interaction.send(content=f"Successfully updated image to {image}")
                    elif isinstance(image, int):
                        db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$unset":{"image":""}})
                            
                        await interaction.send(content="Successfully removed image.")
                        
                elif int(value) == 6:
                    await interaction.send("Please send link for your thumbnail icon (if you want remove image just send `0` or `no`)")
                    image ,msg = await helpers.waitforrespon(self,interaction.channel,interaction.user,"image_n",180)
                    if isinstance(image, str):
                            db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$set":{"icon":image}})
                            
                            await interaction.send(content=f"Successfully updated thumbnail icon to {image}")
                            
                    elif isinstance(image, int):

                            db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$unset":{"icon":""}})
                            await interaction.send(content="Successfully removed thumbnail icon.")
                            
                        
                        
                            
                elif int(value) == 7:
                    await interaction.send("Please send what u want to have in title")
                    msg = await helpers.waitforrespon(self,interaction.channel,interaction.user,"msg",180)
                    if msg:
                        
                        db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$set":{"title":msg.content}})
                        await interaction.send(content=f"Successfully updated title to {msg.content}")
                        

                elif int(value) == 8:
                    await interaction.send("Please send link for your footer  icon (if you want remove image just send `0` or `no`)")
                    image ,msg = await helpers.waitforrespon(self,interaction.channel,interaction.user,"image_n",180)
                    if isinstance(image, str):
                        db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$set":{"footer-icon":image}})
                        
                        await interaction.send(content=f"Successfully updated footer icon to {image}")
                            
                    elif isinstance(image, int):
                        db.embedstylesdb.update_one({"_id":styledb["_id"]}, {"$unset":{"footer-icon":""}})
                        
                        await interaction.send(content="Successfully removed footer icon.")
                            
                        
                    else:
                        embed=Embed(title="ERROR | incorrect link", description="Cancelled the Operation!", color=0xff0000)
                        if interaction.guild is not None or interaction.guild.icon.url is not None:
                            embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                            await interaction.edit_original_message(embed=embed)
                if value == "00":

                    
                    
                    await setup_settings.presetup2_menu(self,interaction)
            
                else :
                    
                    
                    await setup_settings.setupstylehead_menu(self,interaction)
                    

                    await headcategorycs.refreshlables(self,interaction.guild_id)


            else:
                embed=Embed(title="Error", description="**First you must setup the `setup required`**", color=0xfffff0)
                await interaction.send(embed=embed, ephemeral=True)




class presetup2(nextcord.ui.Select):
    def __init__(self,bot:Bot,):
        self.bot  = bot
        selectOption = [
            nextcord.SelectOption(label="Setup head-Category ui", emoji="⚙️" ,value=1, ),
            #nextcord.SelectOption(label="Setup sub-Category ui", emoji="🗃️" ,value=2, ),
            #nextcord.SelectOption(label="Setup products ui", emoji="🗃️" ,value=3, ),
            #nextcord.SelectOption(label="Setup ticket ui", emoji="🗃️" ,value=4, ),
            nextcord.SelectOption(label="Go Back",emoji="🔙", value = "00",)


        ]
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0]
        
        

        if int(value) == 1:
            await setup_settings.setupstylehead_menu(self,interaction)
            

        elif int(value) == 2:
            pass
        
        elif value == "00":
            await interaction.message.edit(content=embeds["1-Setup"]["content"],embed=None, view=sview(self.bot,presetup, interaction.user, 120))

    
class presetup(nextcord.ui.Select):
    def __init__(self,bot:Bot,):
        self.bot = bot
        selectOption = [
            nextcord.SelectOption(label="Setup-style", emoji="1️⃣" ,value="1", ),
            nextcord.SelectOption(label="Setup-Head-Category", emoji="2️⃣" ,value="2", ),
            nextcord.SelectOption(label="Payments", emoji="3️⃣" ,value="3", ),
            nextcord.SelectOption(label="Your Goods", emoji="4️⃣" ,value="4", ),
            
            
         
            
            
           

        ]
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0]
        
        
        if int(value) == 1:
            embed=Embed(title="Embed stile editor", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
            embed.set_image(url=config.IMAGE_STYLE_TUTORIAL)
            await interaction.message.edit(embed=embed, view=sview(self.bot,presetup2, interaction.user, 120))
            

        elif int(value) == 2:
            
            await setup_settings.setup_menu(self,interaction )
                    
            
        elif int(value) == 3:
            await interaction.response.defer()
            await setup_settings.presetup_menu(self,interaction)
        elif int(value) == 4:
            goods = list(db.goodsdb.find( { "type": { "$not": { "$regex": "^keys.*" } } } ))
            selectOption = []
            emojilist = ["🔴","🟠","🟡","🟢","🔵","🟣","🟤","⚫","⚪"]
            count = 0
            for good in goods:
                selectOption.append(nextcord.SelectOption(label=good["label"],emoji=emojilist[count], value=f'{good["_id"]}',))
                count +=1
            selectOption.append(nextcord.SelectOption(label="Keys", emoji="3️⃣" ,value="keys", ),)
            selectOption.append(nextcord.SelectOption(label="Files", emoji="4️⃣" ,value="files", ),)
            selectOption.append(nextcord.SelectOption(label="Add good",emoji=f"{config.EMOJI_ADD} ", value="add",))
            embed = nextcord.Embed(title="Goods Manager", description="**Select what you need in the `Selection` down Below!**", color=Colour.brand_green(), timestamp=datetime.datetime.now(),)
            await interaction.send(embed=embed, view=sview(self.bot,goodsmanager,interaction.user,120,selectOption))

  
class goodsmanager(nextcord.ui.Select):
    def __init__(self,bot:Bot,selectOption):
        self.bot = bot 
        
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0]
        if value == "add":
            gmdb =  list(db.goodsdb.find({"guilds":interaction.guild_id}))
            embed = nextcord.Embed(title="Goods Templates", description="**Select what you need in the `Selection` down Below!**", color=Colour.yellow(), timestamp=datetime.datetime.now(),)
            selectOption = []
            commendbot_smart = list(filter(lambda i: i['type'] == "commendbot", gmdb))
            if len(commendbot_smart) == 0:
                selectOption.append(nextcord.SelectOption(label="CommendBot Template", emoji="1️⃣" ,value="1", ),)
            senpay = list(filter(lambda i: i['type'] == "senpay", gmdb))
            if len(senpay) == 0:
                selectOption.append(nextcord.SelectOption(label="Steam Services Template", emoji="2️⃣" ,value="2", ),)
            ranksmm = list(filter(lambda i: i['type'] == "ranksmm", gmdb))
            if len(ranksmm) == 0:
                selectOption.append(nextcord.SelectOption(label="Ranks Template", emoji="3️⃣" ,value="3", ),)
            

            await interaction.send(embed=embed,view=sview(self.bot,goodsadd,interaction.user,120,selectOption))
        elif value == "keys":
            selectOption = []
            number = 0
            description ="Select key category\n"
            db.keysdbs = list(db.goodsdb.find({"guilds":interaction.guild_id,"type":"keys"}))
            print(len(db.keysdbs))
            for baldb in db.keysdbs:
                
                
                
                
                number += 1     
                description += f"\n{number}. {baldb['label']}"
                selectOption.append(nextcord.SelectOption(label=f"{number}. {baldb['label']}" ,value=f"{baldb['_id']}" ))
                

                
            selectOption.append(nextcord.SelectOption(label="Add category",emoji=f"{config.EMOJI_ADD} ", value="add",))
            embed = nextcord.Embed(title="All yours keys lib", description=description, color=Colour.brand_green(), timestamp=timestamp,)
            await interaction.send(embed=embed, view=sview(self.bot, subkeys , interaction.user,120,selectOption))  
  
class subkeys(nextcord.ui.Select):
    def __init__(self,bot:Bot,selectOption):
        self.bot = bot 
        
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):     
        value = self.values[0]
        if value == "add":
            embed = nextcord.Embed(title="Please send  category name", description="Please send in to chat name category for keys ", color=Colour.yellow(), timestamp=timestamp,)
            await interaction.send(embed=embed)
            msg =  await helpers.waitforrespon(self,interaction.channel,interaction.user,"msg",180)
            if msg:
                name = msg.content
                if len(name) <= 50: 
                    
                    trys = list(db.goodsdb.find({"guilds":interaction.guild_id,"label":name, "type":"keys"}))
                    if len(trys) == 0 :
                        _id = db.goodsdb.insert_one({"guilds":[interaction.guild.id],"label":name,"type":"keys"}).inserted_id
                        await setup_settings.keysdb(self,interaction,_id)
                        
                                
                    else:
                        embed = nextcord.Embed(title="Error - Name is incorrect", description="This name is used!", color=Colour.red(), timestamp=timestamp,)
                        await interaction.send(embed=embed)
                        # here put refresh labels
                else:
                    
                    embed = nextcord.Embed(title="Error - Name is Too long!", description="This name is too long", color=Colour.red(), timestamp=timestamp,)
                    await interaction.send(embed=embed)
        else:
            _id = ObjectId(value)
            await setup_settings.keysdb(self,interaction,_id)
            
            
class keysdatabase(nextcord.ui.Select):
    def __init__(self,bot:Bot,selectOption,databaseid):
        self.databaseid =databaseid
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0]
        databaseid = self.databaseid
        if value == "add": 
            embed = nextcord.Embed(title="Please send  subcategory name", description="Please send in to chat name subcategory for keys ", color=Colour.yellow(), timestamp=timestamp,)
            await interaction.send(embed=embed)
            msg =  await helpers.waitforrespon(self,interaction.channel,interaction.user,"msg",180)
            if msg:
                name = msg.content
                if len(name) <= 50: 
                    
                    trys = list(db.subkeys.find({"guildid":interaction.guild_id,"label":name, "type":"keys"}))
                    if len(trys) == 0 :
                        _id = db.subkeys.insert_one({"guildid":interaction.guild.id,"label":name,"database":ObjectId(databaseid)}).inserted_id
                        await setup_settings.addkeys(self,interaction.channel,interaction.user,databaseid,_id)
                        
                                
                    else:
                        embed = nextcord.Embed(title="Error - Name is incorrect", description="This name is used!", color=Colour.red(), timestamp=timestamp,)
                        await interaction.send(embed=embed)
                        # here put refresh labels
                else:
                    
                    embed = nextcord.Embed(title="Error - Name is Too long!", description="This name is too long", color=Colour.red(), timestamp=timestamp,)
                    await interaction.send(embed=embed)
            
        else:
            selectOption = []
            database = db.subkeys.find_one({"_id":ObjectId(value)})
            
            selectOption.append(nextcord.SelectOption(label="Change name" ,value="1" ))
            selectOption.append(nextcord.SelectOption(label="Add key/s",emoji=f"{config.EMOJI_ADD} ", value="add",))
            selectOption.append(nextcord.SelectOption(label="Edit keys" ,value="2" ))
            selectOption.append(nextcord.SelectOption(label="delete subdatabase" ,value="3" ))
            embed = nextcord.Embed(title=f"{database['label']} database manager",  color=Colour.blurple(), timestamp=timestamp,)
            await interaction.send(embed=embed , view=sview(self.bot, keysmanager , interaction.user, 120,selectOption,databaseid,database['_id']))
       
class keysmanager(nextcord.ui.Select):
    def __init__(self,bot:Bot,selectOption,databaseid,subdatabaseid):
        self.bot = bot 
        self.databaseid =databaseid
        self.subdatabaseid =subdatabaseid 
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0]
        databaseid =ObjectId(self.databaseid)
        if value == "add":
            
            pass
        elif value == "1":
            
            await setup_settings.addkeys(self,interaction.channel,interaction.user,databaseid,interaction)
        
        elif value == "2":
            selectOption = []
            description = "Select key to edit"
            number = 0
            keylib = list(db.keysdb.find({"database":ObjectId(databaseid)}))
            for baldb in keylib:
                    
                    
                    
                    
                    number += 1     
                    description += f"\n key {number}. - ||{baldb['key']}||"
                    selectOption.append(nextcord.SelectOption(label=f"key {number}" ,value=f"{baldb['_id']}" ))
                    
            embed = nextcord.Embed(title=f"Please type in chat/dms number of key(1-{number})", description=description, color=Colour.gold(), timestamp=timestamp,)
            option = await can_dm_user(interaction.user)
            if option:
                await interaction.send("Check your dms!")
                await interaction.user.send(embed = embed)
                number, msg  = await helpers.waitforrespon(self,interaction.user,interaction.user,"int",120 )
                
            else:
                await interaction.send(embed = embed)
                number , msg = await helpers.waitforrespon(self,interaction.channel,interaction.user,"int",120 )
            if number and msg:
                id = keylib[number-1]["_id"]
                
                
            
            
                
            
                selectOption = []
                selectOption.append(nextcord.SelectOption(label="Show key" ,value="show" ))
                selectOption.append(nextcord.SelectOption(label="edit key" ,value="edit" ))
                selectOption.append(nextcord.SelectOption(label="transfer key" ,value="transfer" ))
                selectOption.append(nextcord.SelectOption(label="delete key" ,value="del" ))
                embed = nextcord.Embed(title="Key manager",  color=Colour.blurple(), timestamp=timestamp,)
                if option:
                    await interaction.user.send(embed=embed , view=sview(self.bot, keyssettings , interaction.user, 120,selectOption, id))
                else:
                    await interaction.channel.send(embed=embed , view=sview(self.bot, keyssettings , interaction.user, 120,selectOption, id))
            
        
            
        
        
        

        
        

class keyssettings(nextcord.ui.Select):
    def __init__(self,bot:Bot,selectOption, keyid):
        self.bot = bot 
        self.keyid =keyid
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        keyid = self.keyid
        value = self.values[0]
        keydb = db.keysdb.find_one({"_id":ObjectId(keyid)}) # it is in obid but whatever
        
        if value == "show":
            embed = nextcord.Embed(title="Your key is: ", description=f"`{keydb['key']}`", color=Colour.green(), timestamp=timestamp,)
            await interaction.send(embed=embed)
        elif value == "edit":
            embed = nextcord.Embed(title="Please send your new key", description="Please send me ur key in this chat or in me dms!", color=Colour.gold(), timestamp=timestamp,)
            embed.add_field(name="Old key:", value=f"`{keydb['key']}`", inline=False)
            await interaction.send(embed=embed)
            msg  = await helpers.waitforrespon(self,interaction.user,interaction.user,"msg",120 )
            if msg:
                db.keysdb.update_one({'userid': interaction.user.id}, {'$set': {'key': msg.content}})
                embed = nextcord.Embed(title="Your key was changed!", description=f"New key: ||{msg.content}||", color=Colour.green(), timestamp=timestamp,)
                await interaction.channel.send(embed=embed)
        elif value == "del":
            embed=Embed(description="**Hey, be careful!** The following actions will be taken on this server and can not be undone: \n- Key ll be deleted")
            embed.set_author(name="Warning", icon_url=config.IMAGE_WARNING_ICON)
            view = Confirm_clear()
            await interaction.message.edit(embed=embed, view=view)
            await view.wait()
            if view.value is None:
                embed=Embed(description="**Hey, be careful!** The following actions will be taken on this server and can not be undone: \n- Key ll be deleted")
                embed.set_author(name="Warning", icon_url=config.IMAGE_WARNING_ICON)
                await interaction.channel.send(embed=embed, view=None,delete_after=30)
            elif view.value:
                pass
                
        
        
        



      
  
class slotsview(nextcord.ui.Select):
    def __init__(self,bot:Bot,selectOption):
        self.bot = bot 
        
        super().__init__(placeholder="select:", min_values=1, max_values=len(selectOption), options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.defer()
        ids = ""
        print(self.values[0])
        for slotid in self.values[0]:
            if slotid == "0":
                ids = "0"
                break
            else:
                ids += f"{slotid}-"
        await setup_settings.commendbotsetup(self,interaction,ids)  
  
  
  
class goodsadd(nextcord.ui.Select):
    def __init__(self,bot:Bot,selectOption):
        self.bot = bot 
        
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        type = self.values[0]
        subdbs = db.subdb.find_one({"ownerid":interaction.user.id,"disabled":False})
        if  subdbs:
                
            if type == "1":
                balsdb = list(db.balancesdb.find({"userid":interaction.user.id}))
                if len(balsdb) == 1:
                    slots = "0"
                    await setup_settings.commendbotsetup(self,interaction,slots)
                    
                elif len(balsdb) == 0:    
                    embed = nextcord.Embed(title="Alert ", description="You dont have any balance in <@937729933571149847>", color=Colour.red(), timestamp=timestamp,)
                    await interaction.send(embed=embed)
                    
                else:
                    emojilist = ["🔴","🟠","🟡","🟢","🔵","🟣","🟤","⚫","⚪"]
                    selectOption = []
                    number = 0
                    description ="Select slot what do you wanna use for giving the commends "
                    for baldb in balsdb:
                        
                        
                        slot = db.slotsdb.find_one({"_id":baldb["slot_id"]})
                        if slot["enable"]:
                            
                            description += f"\n{emojilist[number]}-{slot['_id']}. {slot['name']}・ {baldb['amount']} commends"
                            selectOption.append(nextcord.SelectOption(label=f"{slot['_id']}. {slot['name']} - {baldb['amount']} commends",emoji=emojilist[number] ,value=f"{slot['_id']}" ))
                        else:
                            description += f"\n__**This Slot is disabled**__ = ~~{emojilist[number]}-{slot['_id']}. {slot['name']}・ {baldb['amount']} commends~~ "

                        number += 1 
                    selectOption.append(nextcord.SelectOption(label="All slots",emoji="💢" ,value="0" ))
                    embed = nextcord.Embed(title="Select Slot", description=description, color=Colour.blurple(), timestamp=timestamp,)
                    await interaction.send(embed=embed, view=sview(self.bot,slotsview, interaction.user,120,selectOption))
            elif type == "2":
                pass # here pase code for tf2 keys setup
            elif type == "3":
                db.goodsdb.insert_one({"guilds":[interaction.guild_id],"label":"RankBoost MM","type":"ranksmm","ranks":{"1":2,"2":2,"3":2,"4":2,"5":2,"6":2,"7":2,"8":2,"9":2,"10":2,"11":2,"12":2,"13":2,"14":2,"15":2,"16":2,"17":2,"18":2,}})

        else:
              embed = nextcord.Embed(title="You dont have resell sub", description=f"You dont have commendbot resell sub!(buy [here]({config.BRAND_URL}/product/csgo-commendbot-resell/))", color=Colour.orange(), timestamp=timestamp,)   
              await interaction.send(embed=embed)           


  
class paymentssetup(nextcord.ui.Select):
    def __init__(self,bot,selectOption):
        self.bot :Bot = bot 
        
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)  

    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0]
        
        
            
        if value == "add":
            embed=Embed(title="What name(title) do you wanna use?", description="Just send in the Chat category name", color=0x23929a)
            embed.set_image(url=config.IMAGE_PRODUCT_TUTORIAL)
            if  interaction.guild  or interaction.guild.icon is not None:
                    embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
            await interaction.message.edit(embed=embed,view=None)

            try:
                text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
            except asyncio.exceptions.TimeoutError:
                embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                if interaction.guild is not None or interaction.guild.icon.url is not None:
                    embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                await interaction.send(embed=embed)
                # add back to menu
            else:
                await text.delete()
                category_name = text.content
                embed=Embed(title="What description do you wanna use?", description="Just send in the Chat description **if you want category without a description just send `0` or `no` in this channel**", color=0x23929a)
                embed.set_image(url=config.IMAGE_PRODUCT_TUTORIAL)
                if interaction.guild is not None or interaction.guild.icon.url is not None:
                    embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                await interaction.message.edit(embed=embed)
                try:
                    text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
                except Exception:
                    embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                    if interaction.guild is not None or interaction.guild.icon.url is not None:
                        embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                    await interaction.send(embed=embed)
                    # add back to menu
                else:
                    await text.delete()
                    if not "0" == text.content or not "no" == text.content:
                        category_description = text.content

                    embed=Embed(title="What emoji do you wanna use?", description="Just __**react**__ with your emoji(only server emojis or default emojis)", color=0x23929a)
                    embed.set_image(url=config.IMAGE_PRODUCT_TUTORIAL)
                    if interaction.guild is not None or interaction.guild.icon.url is not None:
                            embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                    msg = await interaction.message.edit(embed=embed)

                    try:
                        reaction , user = await self.bot.wait_for("reaction_add", check=lambda reaction,user: reaction.message.id ==interaction.message.id and user.id == interaction.user.id, timeout=180)
                    except Exception:
                        embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                        if interaction.guild is not None or interaction.guild.icon.url is not None:
                            embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                        await interaction.send(embed=embed)
                    else:
                        product_emoji = str(reaction)
                        await interaction.message.remove_reaction(product_emoji, interaction.user)
                        
                        testvalue = product_emoji.replace(">" , "").split(":")
                        if 2 in testvalue :
                            testvalue = int(testvalue[2])
                            
                            
                            emoji = self.bot.get_emoji(testvalue)
                            
                            if emoji is not None:
                                
                                embed=Embed(title="What text msg do you wanna use?(when customer set this payment get this text)", description="send here", color=0x23929a)
                
                                if interaction.guild is not None or interaction.guild.icon.url is not None:
                                        embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                                msg = await interaction.message.edit(embed=embed)

                                try:
                                    text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
                                except Exception:
                                    embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                                    if interaction.guild is not None or interaction.guild.icon.url is not None:
                                        embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                                    await interaction.channel.send(embed=embed)
                                    
                                else:
                                    await interaction.message.delete()
                                    print("here")
                                    text_msg = text.content
                                    

                                    
                                    if category_description:
                                        db.paymentsdb.insert_one({"guildid":interaction.guild_id, "label":category_name, "emoji":product_emoji,"description":category_description, "text":text_msg})
                                        
                                    else:
                                        db.paymentsdb.insert_one({"guildid":interaction.guild_id, "label":category_name, "emoji":product_emoji, "text":text_msg})
                                        
                                        
                                    await interaction.send(content="Successfully add")
                                    
                            else:
                                embed=Embed(title="ERROR | This emoji isnt on your server!", description="Cancelled the Operation!", color=0xff0000)
                                if interaction.guild is not None or interaction.guild.icon.url is not None:
                                    embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                                await interaction.channel.send(embed=embed)
                                #add back to mneu 
                        else:
                                emoji = testvalue[0]
                                if emoji is not None:
                                
                                    embed=Embed(title="What text msg do you wanna use?(when customer set this payment get this text)", description="send here", color=0x23929a)
                
                                    if interaction.guild is not None or interaction.guild.icon.url is not None:
                                            embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                                    await interaction.message.edit(embed=embed)

                                    try:
                                        text: nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
                                    except Exception:
                                        embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                                        if interaction.guild is not None or interaction.guild.icon.url is not None:
                                            embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                                        await interaction.channel.send(embed=embed)
                                    else:
                                        await text.delete()
                                        print("here")
                                        text_msg = text.content
                                        

                                        
                                        if category_description:
                                            db.paymentsdb.insert_one({"guildid":interaction.guild_id, "label":category_name, "emoji":product_emoji,"description":category_description, "text":text_msg})
                                        
                                        else:
                                            db.paymentsdb.insert_one({"guildid":interaction.guild_id, "label":category_name, "emoji":product_emoji, "text":text_msg})
                                            
                                            
                                        await interaction.channel.send(content="Successfully add",delete_after=10)
                                else:
                                    embed=Embed(title="ERROR | incorrect emoji", description="Cancelled the Operation!", color=0xff0000)
                                    if interaction.guild is not None or interaction.guild.icon.url is not None:
                                        embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                                    await interaction.channel.send(embed=embed)
        elif value == "00":
            await interaction.message.edit(content=embeds["1-Setup"]["content"],embed=None, view=sview(self.bot,presetup, interaction.user, 120))

                        

        else:
            print(f"lesss {value}")
            embed=Embed(title="Embed stile editor payments", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
            await interaction.message.edit(embed=embed, view=sview(self.bot,paymentseditit,interaction.user,120 ))
            
                
class setupcategory(nextcord.ui.Select):
    def __init__(self,bot:Bot,  selectOption,hcategory):
        self.bot = bot
            
         
            
            
           
        self.hcategory = hcategory
        
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0]
        hcategory = self.hcategory
        back=True
    
        if int(value) == 1:

            embed=Embed(title="What name(title) do you wanna use?", description="Just send in the Chat category name", color=0x23929a)
            embed.set_image(url=config.IMAGE_PRODUCT_TUTORIAL)
            if interaction.guild is not None or interaction.guild.icon.url is not None:
                    embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
            await interaction.send(embed=embed)
            
            try:
                text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
            except Exception:
                embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                if interaction.guild is not None or interaction.guild.icon.url is not None:
                    embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                await interaction.edit_original_message(embed=embed)
            else:
                category_name = text.content
                embed=Embed(title="What description do you wanna use?", description="Just send in the Chat description **if you want category without a description just send `0` or `no` in this channel**", color=0x23929a)
                embed.set_image(url=config.IMAGE_PRODUCT_TUTORIAL)
                if interaction.guild is not None or interaction.guild.icon.url is not None:
                    embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                await interaction.send(embed=embed)
                try:
                    text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
                except Exception:
                    embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                    if interaction.guild is not None or interaction.guild.icon.url is not None:
                        embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                    await interaction.send(embed=embed)
                else:
                    if not "0" == text.content or not "no" == text.content:
                        category_description = text.content

                    embed=Embed(title="What emoji do you wanna use?", description="Just __**react**__ with your emoji(only server emojis or default emojis)", color=0x23929a)
                    embed.set_image(url=config.IMAGE_PRODUCT_TUTORIAL)
                    if interaction.guild is not None or interaction.guild.icon.url is not None:
                            embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                    msg = await interaction.channel.send(embed=embed)

                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction,user: reaction.message.id == msg.id and user.id == interaction.user.id, timeout=180)
                    except Exception:
                        embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                        if interaction.guild is not None or interaction.guild.icon.url is not None:
                            embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                        await interaction.channel.send(embed=embed)
                    else:
                        
                        
                        product_emoji = str(reaction)
                        testvalue = product_emoji.replace(">" , "").split(":")
                        if 2 in testvalue :
                            testvalue = int(testvalue[2])
                            
                            
                            emoji = self.bot.get_emoji(testvalue)
                            
                            if emoji is not None:
                                test_value = db.headcategorysdb.find_one({"guildid":interaction.guild_id,"headcategory":f"category{hcategory}"})
                                if test_value is None:
                                    
                                    if category_description is not None:
                                        
                                        db.headcategorysdb.insert_one({"guildid":interaction.guild_id,"headcategory":f"category{hcategory}","label":category_name  , "emoji":product_emoji})
                                        
                                        
                                    else:
                                        db.headcategorysdb.insert_one({"guildid":interaction.guild_id, "headcategory":f"category{hcategory}","label":category_name  , "emoji":product_emoji,"description":category_description})
                                    
                                    await headcategorycs.refreshlables(self,interaction.guild_id)
                                    await interaction.send(f"**{config.EMOJI_YES}  Added the Category to the menu**")
                                else:
                                    await interaction.send(f"**{config.EMOJI_NO}  u cant setup category what was setup!**")
                            else:
                                embed=Embed(title="ERROR | This emoji isnt on your server!", description="Cancelled the Operation!", color=0xff0000)
                                if interaction.guild is not None or interaction.guild.icon.url is not None:
                                    embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                                await interaction.channel.send(embed=embed)
                        else:
                                emoji = testvalue[0]
                                if emoji is not None:
                                    test_value = db.headcategorysdb.find_one({"guildid":interaction.guild_id,"headcategory":f"category{hcategory}"})
                                    if test_value is None:
                                        
                                        if category_description is not None:
                                            
                                            db.headcategorysdb.insert_one({"guildid":interaction.guild_id,"headcategory":f"category{hcategory}","label":category_name  , "emoji":product_emoji})
                                            
                                            
                                        else:
                                            db.headcategorysdb.insert_one({"guildid":interaction.guild_id, "headcategory":f"category{hcategory}","label":category_name  , "emoji":product_emoji,"description":category_description})
                                        
                                        await headcategorycs.refreshlables(self,interaction.guild_id)
                                        await interaction.send(f"**{config.EMOJI_YES}  Added the Category to the menu**")
                                    else:
                                        await interaction.send(f"**{config.EMOJI_NO}  u cant setup category what was setup!**")
                                else:
                                    embed=Embed(title="ERROR | incorrect emoji!", description="Cancelled the Operation!", color=0xff0000)
                                    if interaction.guild is not None or interaction.guild.icon.url is not None:
                                        embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                                    await interaction.channel.send(embed=embed)

        elif int(value) == 2:
            back =False
            embed=Embed(title="Events Setup", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
            await interaction.send(embed=embed, view=sview(self.bot,eventsm, interaction.user, 120,hcategory))
        elif int(value) == 3:
            back =False
            await setup_settings.subcategorys_setup(self,interaction, hcategory)
            
        elif int(value) == 4:
            
            
            events = db.headcategorysdb.find_one({"guildid":interaction.guild_id, "headcategory":f"category{hcategory}"})
            if events is not None:
                spcategory = events
                
                
                if "subcategory" not in spcategory["run"]: 
                    back =False
                    await setup_settings.productsmanager(self,interaction,hcategory)
                else:
                    embed=Embed(title="ERROR | You have setup incorrect event in events for this category!", description="if u want add or change product in this category you need set in events to show products \nor if u want add or change product in subcategory just go in Categorys Setup: ` subCategory > subCategory1-8 > Products` ", color=0xff0000)
                    if interaction.guild is not None or interaction.guild.icon.url is not None:
                        embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                    await interaction.send(embed=embed)

            else:
                await interaction.send(f"You dont have set category named category{hcategory}")
        elif int(value) == 5:
            menu = db.headcategorysdb.find_one({"headcategory":f"category{hcategory}", "guildid":interaction.guild_id,})
            if menu is not None:
            
                
                if menu["enabled"]:
                    
                    await interaction.send(f"  category {hcategory} is now Disabled{config.EMOJI_NO}! ",delete_after=30)
                else:
                    await interaction.send(f" category {hcategory} is now Enabled{config.EMOJI_YES}! ",delete_after=30)
                    
                db.headcategorysdb.update_one({"guildid":interaction.guild_id,"headcategory":f"category{hcategory}"}, {"$set":{"enabled":(not menu["enabled"])}})

                
            

            else:
                await interaction.send(f"You dont have set category named category{hcategory}",delete_after=30)

        elif int(value) == 6:     
            embed=Embed(description="**Hey, be careful!** The following actions will be taken on this server and can not be undone: \n- All **existing products** in this category will be **deleted**\n- All **existing subCategories** in this category will be **deleted**\n- All **settings for category** will be **deleted**")
            embed.set_author(name="Warning", icon_url=config.IMAGE_WARNING_ICON)
            view = Confirm_clear(self.bot)
            await interaction.message.edit(embed=embed, view=view)
            # Wait for the View to stop listening for input...
            await view.wait()
            if view.value is None:
                embed=Embed(description="**Hey, be careful!** The following actions will be taken on this server and can not be undone: \n- All **existing products** in this category will be **deleted**\n- All **existing subCategories** in this category will be **deleted**\n- All **settings for category** will be **deleted**")
                embed.set_author(name="Warning", icon_url=config.IMAGE_WARNING_ICON)
                await interaction.channel.send(embed=embed, view=None,delete_after=30)
            elif view.value:
                print("Confirmed...")
                db.productsdb.delete_many({"guildid":interaction.guild_id, "headcategory": f"category{hcategory}"})
                
                db.subcategoriesdb.delete_many({"guildid":interaction.guild_id, "headcategory":f"category{hcategory}" })
                db.headcategorysdb.delete_many({"guildid":interaction.guild_id, "headcategory":f"category{hcategory}"})
                db.embedstylesdb.delete_many({"guildid":interaction.guild_id, "headcategory":f"category{hcategory}"})
                await interaction.channel.send(f"**The category was successfully deleted with all data{config.EMOJI_YES}**",delete_after=30)
            else:
                print("Cancelled...")
        elif int(value) == 8:
            pass 
        elif int(value) == 9:
            await style.setupstylesub_menu(self,interaction,hcategory)
        elif int(value) == 10:
            await style.setupstyleproducts_menu(self,interaction,hcategory)
        if value == "00":

                    
                    await setup_settings.setup_menu(self,interaction)
                    
        else :
            if back:
                    
                    
                    embed=Embed(title="Embed stile editor payments", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
                    await interaction.message.edit(embed=embed, view=sview(self.bot,paymentseditit,interaction.user,120 ))
                    await setup_settings.headcategorysetup_menu(self,interaction,hcategory)


class eventsm(nextcord.ui.Select):
    def __init__(self,bot:Bot,hcategory):
        self.bot = bot 
        selectOption = [
            nextcord.SelectOption(label="Setup/Change Event", emoji="⚙️" ,value="1", ),
            nextcord.SelectOption(label="Change Server Category", emoji="🗂️" ,value="2", ),
            nextcord.SelectOption(label="Go Back",emoji="🔙", value = "00",)

        ]
        self.hcategory = hcategory
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0]
        hcategory =self.hcategory
        view =None

        if int(value) == 1:
            embed=Embed(title="What server category do you wanna use?", description="Just send in the Chat `category name` or `category id`", color=0x23929a)
            if interaction.guild  and  interaction.guild.icon.url :
                    embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
            await interaction.send(embed=embed)
            try:
                    text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=250)
            except Exception:
                    embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                    if  interaction.guild  and  interaction.guild.icon.url :
                        embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                    await interaction.send(embed=embed)
            else:
                idss =text.content
                if idss.isnumeric() is True:
                    

                    category = get(interaction.guild.categories, id=int(idss))
                    
                else:
                    category = get(interaction.guild.categories, name=idss)
                if category is None:
                    embed=Embed(title="ERROR | Incorrect server category id/name", description="Cancelled the Operation!", color=0xff0000)
                    await interaction.send(embed=embed)
                else:
                    db.headcategorysdb.update_one({"guildid":interaction.guild_id, "headcategory":f"category{hcategory}"}, {"$set":{"categoryid":category.id}})
                    
                    await headcategorycs.refreshlables(self,interaction.guild_id)
                    await interaction.send(f"**{config.EMOJI_YES}  Successfuly changed option!**")
                    embed=Embed(title="What do after customer click to category option.", description="**Select what you need in the `Selection` down Below!** ", color=0x23929a)
                    view =sview(self.bot,selectevent,interaction.user,120,hcategory)
                    
                    await interaction.send(embed=embed,view=view)
                    

        elif int(value) == 2:
            event = db.headcategorysdb.find_one({"guildid":interaction.guild_id, "headcategory":f"category{hcategory}"}) 
            if event  and "categoryid" in event:
                embed=Embed(title="What server category do you wanna use?", description="Just send in the Chat category name or category id", color=0x23929a)
                if interaction.guild is not None or interaction.guild.icon.url is not None:
                        embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                await interaction.send(embed=embed)
                try:
                        text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=250)
                except Exception:
                        embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                        if interaction.guild is not None or interaction.guild.icon.url is not None:
                            embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                        await interaction.send(embed=embed)
                else:
                    idss =text.content
                    if idss.isnumeric() is True:
                        category = get(interaction.guild.categories, id=int(idss))
                    else:
                        category = get(interaction.guild.categories, name=idss)
                    if category is None:
                        embed=Embed(title="ERROR | Incorrect server category id/name", description="Cancelled the Operation!", color=0xff0000)
                        await interaction.send(embed=embed)
                    else:
                        db.headcategorysdb.update_one({"_id": event["_id"]}, {"$set":{"categoryid":category.id}})
                        
                        await headcategorycs.refreshlables(self,interaction.guild_id)                                                        
                        await interaction.send(f"**{config.EMOJI_YES}  Successfuly changed option!**")
            else:
                embed=Embed(title="ERROR | First setup events!", description="Cancelled the Operation!", color=0xff0000)
                if interaction.guild is not None or interaction.guild.icon.url is not None:
                    embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                await interaction.send(embed=embed)
        if value == "00":
            await setup_settings.headcategorysetup_menu(self,interaction,hcategory)
            
        else :
            if view is None:
                embed=Embed(title="Events Setup", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
                await interaction.send(embed=embed, view=sview(self.bot,eventsm, interaction.user, 120,hcategory))
                


   
class paymentseditit(nextcord.ui.Select):
    def __init__(self,bot:Bot):
        self.bot = bot
        selectOption = [
            #nextcord.SelectOption(label="setup required", emoji="⚙️" ,value=f"1", ),
            nextcord.SelectOption(label="change embed title", emoji="🗃️" ,value="7", ),
            nextcord.SelectOption(label="change embed description", emoji="🗃️" ,value="3", ),
            nextcord.SelectOption(label="change text message", emoji="🗃️" ,value="9", ),
            nextcord.SelectOption(label="delete", emoji="🗃️" ,value="10", ),
            nextcord.SelectOption(label="Go Back",emoji="🔙", value = "00",)

            #nextcord.SelectOption(label="change embed color", emoji="🗃️" ,value=f"2", ),
            #nextcord.SelectOption(label="add/change footer text", emoji="🗃️" ,value=f"4", ),
            #nextcord.SelectOption(label="add/change/remove footer icon", emoji="🗃️" ,value=f"8", ),
            #nextcord.SelectOption(label="add/change/remove embed image", emoji="🗃️" ,value=f"5", ),
            #
            # nextcord.SelectOption(label="add/change/remove thumbnail icon", emoji="🗃️" ,value=f"6", ),
            
            
            
         
            
            
           

        ]
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0]
        

        if int(value) == 2:
            await interaction.message.edit("Please send your specific color in HEX format **with #**")
            color , msg = await helpers.waitforrespon(self,interaction.channel,interaction.user,"hex",180)
            if color:
                    db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"headmenu"}, {"$set":{"color":color}})
                    
                    await interaction.send(content=f"Successfully updated color to {msg.content}")
                        
              
                        
        elif int(value) == 3:
            await interaction.message.edit("Please send what u want to have in description")
            try:
                text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
            except Exception:
                embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                if interaction.guild is not None or interaction.guild.icon.url is not None:
                    embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                    await interaction.send(embed=embed,delete_after=30)
                        
            else:
                db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"headmenu"}, {"$set":{"description":text.content}})
                
                await interaction.channel.send(content=f"Successfully updated description to {text.content}",delete_after=20)
                


        elif int(value) == 4:
            await interaction.message.edit("Please send what u want to have in footer text")
            try:
                text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
            except Exception:
                embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                if interaction.guild is not None or interaction.guild.icon.url is not None:
                    embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                    await interaction.send(embed=embed,delete_after=30)
                        
            else:
                db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"headmenu"}, {"$set":{"footer-text":text.content}})
                
                await interaction.message.edit(content=f"Successfully updated footer-text to {text.content}")
        elif int(value) == 5:
            await interaction.send("Please send link for your image(if you want remove image just send `0` or `no`)")
            try:
                text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
            except Exception:
                embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                if interaction.guild is not None or interaction.guild.icon.url is not None:
                    embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                    await interaction.send(embed=embed,delete_after=30)
                        
            else:
                
                if 'https://' in text.content  or 'http://' in text.content:
                    db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"headmenu"}, {"$set":{"image":text.content}})
                    await interaction.send(content=f"Successfully updated image to {text.content}")
                        
                elif text.content.startswith("0") or text.content.startswith("no"):
                    db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"headmenu"}, {"$unset":{"image":""}})
                    await interaction.send(content="Successfully removed image.")
                        
                
                else:
                    embed=Embed(title="ERROR | incorrect link", description="Cancelled the Operation!", color=0xff0000)
                    if interaction.guild is not None or interaction.guild.icon.url is not None:
                        embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                    await interaction.send(embed=embed)
                        
        elif int(value) == 6:
            await interaction.message.edit("Please send link for your thumbnail icon (if you want remove image just send `0` or `no`)")
            try:
                text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
            except Exception:
                embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                if interaction.guild is not None or interaction.guild.icon.url is not None:
                    embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                    await interaction.send(embed=embed,delete_after=30)
                        
            else:
                
                if 'https://' in text.content  or 'http://' in text.content:
                    db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"headmenu"}, {"$set":{"image":text.content}})
                    await interaction.send(content=f"Successfully updated thumbnail icon to {text.content}",delete_after=30)
                        
                elif text.content.startswith("0") or text.content.startswith("no"):
                    db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"headmenu"}, {"$unset":{"icon":""}})
                    
                    await interaction.send(content="Successfully removed thumbnail icon.",delete_after=30)
                        
                
                else:
                    embed=Embed(title="ERROR | incorrect link", description="Cancelled the Operation!", color=0xff0000)
                    if interaction.guild is not None or interaction.guild.icon.url is not None:
                        embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                    await interaction.send(embed=embed,delete_after=30)
                        
        elif int(value) == 7:
            await interaction.message.edit("Please send what u want to have in title")
            try:
                text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
            except Exception:
                embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                if interaction.guild is not None or interaction.guild.icon.url is not None:
                    embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                await interaction.send(embed=embed,delete_after=30)
                        
            else:
                db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"payments"}, {"$set":{"label":text.content}})
                
                await interaction.send(content=f"Successfully updated title to {text.content}",delete_after=30)
                    

        elif int(value) == 8:
            await interaction.message.edit("Please send link for your footer  icon (if you want remove image just send `0` or `no`)")
            try:
                text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
            except Exception:
                embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                if interaction.guild is not None or interaction.guild.icon.url is not None:
                    embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                await interaction.send(embed=embed,delete_after=30)
                    
            else:
                
                if 'https://' in text.content  or 'http://' in text.content:
                    db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"payments"}, {"$set":{"footer-icon":text.content}})
                    await interaction.send(content=f"Successfully updated footer icon to {text.content}",delete_after=30)
                        
                elif text.content.startswith("0") or text.content.startswith("no"):
                    db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"payments"}, {"$unset":{"footer-icon":""}})
                    
                    
                    await interaction.send(content="Successfully removed footer icon.",delete_after=30)
                    
                
                else:
                    embed=Embed(title="ERROR | incorrect link", description="Cancelled the Operation!", color=0xff0000)
                    if interaction.guild is not None or interaction.guild.icon.url is not None:
                        embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                    await interaction.send(embed=embed,delete_after=30)
                    
    
        elif int(value) == 9:
            await interaction.message.edit("Please send what u want to have in message ")
            try:
                text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user, timeout=180)
            except Exception:
                embed=Embed(title="ERROR | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
                if interaction.guild is not None or interaction.guild.icon.url is not None:
                    embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                await interaction.send(embed=embed,delete_after=30)
                
            else:
                await text.delete()
                db.embedstylesdb.update_one({"guildid":interaction.guild_id, "type":"payments"}, {"$set":{"text":text.content}})
                
                await interaction.send(content=f"Successfully updated title to {text.content}",delete_after=30)
                
        if value == "00":

            
            
            await setup_settings.presetup_menu(self,interaction)
        else :
            
            
            embed=Embed(title="Embed stile editor payments", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
            await interaction.message.edit(embed=embed, view=sview(self.bot,paymentseditit,interaction.user,120 ))




class subsetup(nextcord.ui.Select):
    def __init__(self,bot:Bot,options,hcategory):
        self.bot = bot 

        super().__init__(placeholder="select:", min_values=1, max_values=1, options=options)
        self.hcategory =hcategory
        
    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0]
        hcategory = self.hcategory
        scategory = value
        
        
        if  value != "00":
            await setup_settings.subcategory_menu(self,interaction, hcategory,scategory)
            
        else:

            await setup_settings.headcategorysetup_menu(self,interaction, hcategory)


                           
                

class setup_settings(commands.Cog):
    
    

    def __init__(self, bot: Bot) -> None:
        self.bot = bot 
        
    TESTING_GUILD_ID = [config.STAFF_GUILD_ID] 
    
    
    async def addkeys(self,channel:TextChannel,user:User,hl_id,sub_id,interaction:Interaction=None):
    
        embed = nextcord.Embed(title="Add keys", description="Please send here or in me dms ur codes ", color=Colour.blurple(), timestamp=timestamp,)
        embed.add_field(name="Example", value="key1\nkey2\nkey3\nkey4\n...", inline=False)
        if not interaction:
            await channel.send(embed=embed)
        else:
            await interaction.send(embed=embed)
        msg =  await helpers.waitforrespon(self,channel,user,"msg",180)
        if msg:
            keys =msg.content.split("\n")
            count = 0
            for key in keys:
                count += 1 
                db.keysdb.insert_one({"database":hl_id,"subdatabase":sub_id, "key":key})
                
            embed = nextcord.Embed(title="Successfully Inserted", description=f"We Inserted **{count}** keys in to database", color=Colour.green(), timestamp=timestamp,)
            if can_dm_user(user): 
            
            
                await user.send(embed=embed)
            else:
                await channel.send(embed=embed)
    
    async def keysdb(self,interaction:Interaction,_id):
        selectOption = []
        number = 0
        description ="Select key subcategory\n"
        keysdbs = list(db.subkeys.find({"guildid":interaction.guild.id,"database":_id}))
        print(len(keysdbs))
        for baldb in keysdbs:
            
            
            
            
            number += 1     
            description += f"\n{number}. {baldb['label']}"
            selectOption.append(nextcord.SelectOption(label=f"{number}. {baldb['label']}" ,value=f"{baldb['_id']}" ))
            

            
        selectOption.append(nextcord.SelectOption(label="Add subcategory",emoji=f"{config.EMOJI_ADD} ", value="add",))
        embed = nextcord.Embed(title="All yours keys lib", description=description, color=Colour.brand_green(), timestamp=timestamp,)
        await interaction.send(embed=embed, view=sview(self.bot, keysdatabase , interaction.user,120,selectOption,_id))
        
        
        
    async def setup_menu(self,interaction : nextcord.Interaction):
        embed=Embed(title="Head Category Setup", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
        hcategorys = db.headcategorysdb.find({"guildid":interaction.guild_id})
        hlist =list(hcategorys)
        listnumbers = ["01","02","03","04","05","06","07","08","09","10","11", "12", "13", "14", "15"]
        selectOption = []
        nonelist = {
                "01":nextcord.SelectOption(label="Category", emoji="1️⃣" ,value="01", ),
                "02":nextcord.SelectOption(label="Category", emoji="2️⃣" ,value="02"),
                "03":nextcord.SelectOption(label="Category", emoji="3️⃣" ,value="03"),
                "04":nextcord.SelectOption(label="Category", emoji="4️⃣" ,value="04"),
                "05":nextcord.SelectOption(label="Category", emoji="5️⃣" ,value="05"),
                "06":nextcord.SelectOption(label="Category", emoji="6️⃣" ,value="06"),
                "07":nextcord.SelectOption(label="Category", emoji="7️⃣" ,value="07"),
                "08":nextcord.SelectOption(label="Category", emoji="8️⃣" ,value="08"),
                "09":nextcord.SelectOption(label="Category", emoji="9️⃣" ,value="09"),
                "10":nextcord.SelectOption(label="Category", emoji="🔟" ,value="10"),
                "11":nextcord.SelectOption(label="Category", emoji="<:11:966440104564490330>" ,value="11"),
                "12":nextcord.SelectOption(label="Category", emoji="<:12:966440605024681994>" ,value="12"),
                "13":nextcord.SelectOption(label="Category", emoji="<:13:966440815977189376>" ,value="13"),
                "14":nextcord.SelectOption(label="Category", emoji="<:14:966440948680773643>" ,value="14"),
                "15":nextcord.SelectOption(label="Category", emoji="<:15:966441081271091340>" ,value="15"),

        }
        for tab in listnumbers:
            tale = list(filter(lambda i: i['headcategory'] == f"category{tab}", hlist))
            print(tale)
            
                
            if tale:
                tale = tale[0]
                if "description" in tale:
                    selectOption.append(nextcord.SelectOption(label=tale["label"], description=tale["description"],emoji=tale["emoji"], value=f"{tab}",))
                else:
                    selectOption.append(nextcord.SelectOption(label=tale["label"],emoji=tale["emoji"], value=f"{tab}",))
            else:
                list_value = nonelist[tab]
                selectOption.append(list_value)
        
            


        selectOption.append(nextcord.SelectOption(label="Go Back",emoji="🔙", value = "00",))
        await interaction.message.edit(embed=embed, view=sview(self.bot,setup_view,interaction.user,120,selectOption))
        
        
    async def commendbotsetup(self,interaction:Interaction,slots:str):
        print(slots)
        db.goodsdb.insert_one({"guilds":[interaction.guild_id],"userid":interaction.user.id, "slots":slots,"label":"CommendBot","type":"commendbot"})
        await interaction.send("Your template was inserted to the database, now you need to add/edit products and in goods option select CommendBot")
                        
        
        
    async def setupstylehead_menu(self,interaction: nextcord.Interaction):
        embed=Embed(title="Head-Category Ui", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
        embed.set_image(url=config.IMAGE_STYLE_TUTORIAL)
        await interaction.send(embed=embed, view=sview(self.bot,setupstylehead,interaction.user,120))
        
        
        
    

        

                                    

    async def productsmanager(self,interaction: Interaction,hcategory, scategory=None):
        if scategory:
            products = list(db.productsdb.find({"guildid":interaction.guild_id, "headcategory": f"category{hcategory}", "subcategory":f"subcategory{scategory}"}))
        else:
            products = list(db.productsdb.find({"guildid":interaction.guild_id, "headcategory": f"category{hcategory}"}))
        if len(products) == 0:
            selectOption = [
                nextcord.SelectOption(label="Add product", emoji="⚙️" ,value="1", ),
                nextcord.SelectOption(label="Go Back",emoji="🔙", value = "00",)]
                
        else:
            selectOption = [
                nextcord.SelectOption(label="Add product", emoji="⚙️" ,value="1", ),
                nextcord.SelectOption(label="Change product", emoji="🗂️" ,value="2", ),
                nextcord.SelectOption(label="Delete product", emoji="🗑️" ,value="3", ),
                nextcord.SelectOption(label="Go Back",emoji="🔙", value = "00",)]
        embed=Embed(title="Product Setup 🗂️", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
        await interaction.message.edit(embed=embed, view=sview(self.bot,cateproducts, interaction.user,120,selectOption,hcategory,scategory))

                
        

    async def subcategorys_setup(self,interaction: Interaction, hcategory):
        event2 = db.headcategorysdb.find_one({"guildid":interaction.guild_id , "headcategory":f"category{hcategory}"})
                        
        if event2 :
            if event2["run"] and "subcategory" in event2["run"]:
                embed=Embed(title="subCategory Setup 🗂️ ", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
                scategory = db.subcategoriesdb.find({"guildid":interaction.guild_id,"headcategory":f"category{hcategory}"})
                
                hlist =list(scategory)
                listnumbers = ["1","2","3","4","5","6","7","8", "9"]
                selectOption = []
                nonelist = {
                        "1":nextcord.SelectOption(label="subCategory", emoji="1️⃣" ,value="1", ),
                        "2":nextcord.SelectOption(label="subCategory", emoji="2️⃣" ,value="2"),
                        "3":nextcord.SelectOption(label="subCategory", emoji="3️⃣" ,value="3"),
                        "4":nextcord.SelectOption(label="subCategory", emoji="4️⃣" ,value="4"),
                        "5":nextcord.SelectOption(label="subCategory", emoji="5️⃣" ,value="5"),
                        "6":nextcord.SelectOption(label="subCategory", emoji="6️⃣" ,value="6"),
                        "7":nextcord.SelectOption(label="subCategory", emoji="7️⃣" ,value="7"),
                        "8":nextcord.SelectOption(label="subCategory", emoji="8️⃣" ,value="8"),
                        "9":nextcord.SelectOption(label="subCategory", emoji="9️⃣" ,value="9"),
                        

                }
                for tab in listnumbers:
                    tale = list(filter(lambda i: i['subcategory'] == f"subcategory{tab}", hlist))
                    print(tale)
                    
                        
                    if tale:
                        tale = tale[0]
                        if "description" in tale:
                            selectOption.append(nextcord.SelectOption(label=tale["label"], description=tale["description"],emoji=tale["emoji"], value=f"{tab}",))
                        else:
                            selectOption.append(nextcord.SelectOption(label=tale["label"],emoji=tale["emoji"], value=f"{tab}",))
                    else:
                        list_value = nonelist[tab]
                        selectOption.append(list_value)
                selectOption.append(nextcord.SelectOption(label="Go Back",emoji="🔙", value = "00",))

                await interaction.message.edit(embed=embed, view=sview(self.bot,subsetup, interaction.user,120,selectOption,hcategory))
            else:
                await interaction.send("First setup the events to ",delete_after=30)
        else:
            await interaction.send("First setup the category.",delete_after=30)
            
        
    
    
    async def headcategorysetup_menu(self, interaction: nextcord.Interaction,hcategory:str):
     
    
        test_value = db.headcategorysdb.find_one({"guildid":interaction.guild_id,"headcategory":f"category{hcategory}"})
        if test_value:
            embed=Embed(title=f"{test_value['label']} Setup", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
        else:
            embed=Embed(title=f"Category{hcategory} Setup", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
        selectOption = []
        
        if not hcategory == "00":
            if test_value and "run" in test_value:
                
                selectOption.append(nextcord.SelectOption(label="Category Setup/Change", emoji="⚙️" ,value="1"))
                
                selectOption.append(nextcord.SelectOption(label="Events", emoji="🎫" ,value="2"))
                if "subcategory" in test_value["run"]:
                    
                    selectOption.append(nextcord.SelectOption(label="subCategory", emoji="🗂️" ,value="3"))
                    selectOption.append(nextcord.SelectOption(label="subCategory Style", emoji="🎨" ,value="9"))
                if "products" == test_value["run"]:
                    selectOption.append(nextcord.SelectOption(label="Products Style", emoji="🎨" ,value="10"))
                    selectOption.append(nextcord.SelectOption(label="Products", emoji="🛒" ,value="4"))
                if "ticket" == test_value["run"]:
                    selectOption.append(nextcord.SelectOption(label="Ticket-Settings", emoji="⚙️" ,value="8"))
                selectOption.append(nextcord.SelectOption(label="enable/disable", emoji="💡" ,value="5"))
                selectOption.append(nextcord.SelectOption(label="Clear data", emoji="🔴" ,value="6"))
                selectOption.append(nextcord.SelectOption(label="Cancel", emoji="🔴" ,value="7"))
            elif not test_value:
                selectOption = [
                    nextcord.SelectOption(label="Category Setup/Change", emoji="⚙️" ,value="1"),
                    #nextcord.SelectOption(label="Events", emoji="🎫" ,value=f"2"),
                    #nextcord.SelectOption(label="enable/disable", emoji="💡" ,value=f"5"),
                    nextcord.SelectOption(label="Clear data", emoji="🔴" ,value="6"),
                    nextcord.SelectOption(label="Cancel", emoji="🔴" ,value="7"),
                ]
            else:
                selectOption = [
                    nextcord.SelectOption(label="Category Setup/Change", emoji="⚙️" ,value="1"),
                    nextcord.SelectOption(label="Events", emoji="🎫" ,value="2"),
                    nextcord.SelectOption(label="enable/disable", emoji="💡" ,value="5"),
                    nextcord.SelectOption(label="Clear data", emoji="🔴" ,value="6"),
                    nextcord.SelectOption(label="Cancel", emoji="🔴" ,value="7"),
                    
                ]
            selectOption.append(nextcord.SelectOption(label="Go Back",emoji="🔙", value = "00",))
            await interaction.message.edit(embed=embed, view=sview(self.bot,setupcategory,interaction.user,120,selectOption,hcategory))
        else:
            
            await interaction.message.edit(content=embeds["1-Setup"]["content"],embed=None, view=sview(self.bot,presetup, interaction.user, 120))
        
        
    async def presetup2_menu(self,interaction: nextcord.Interaction):
        embed=Embed(title="Embed stile editor", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
        
        await interaction.message.edit(embed=embed, view=sview(self.bot,presetup2, interaction.user, 120))
        

    
        
    
    async def presetup_menu(self,interaction : nextcord.Interaction):
    
        selectOption = []
        numbers = 0
        embedvalue = ""
        paymethods = db.paymentsdb.find({"guildid":interaction.guild_id})
        if paymethods is not None:
            
            for  value_value in paymethods:
                value_id = str(value_value["_id"])
                numbers = numbers + 1
                valuess = f"{value_id}"
                if "emoji" in value_value:

                    if "description" in value_value and not "0" == value_value["description"]:
                        selectOption.append(nextcord.SelectOption(label=value_value["label"], description=value_value["description"],emoji=value_value["emoji"], value=valuess,))
                        
                    else:
                        selectOption.append(nextcord.SelectOption(label=value_value["label"],emoji=value_value["emoji"], value=valuess))
                    embedvalue = embedvalue + f"{value_value['emoji']}・{value_value['label']}\n\n"
                else:
                    if "description" in value_value and not "0" == value_value["description"]:
                        selectOption.append(nextcord.SelectOption(label=value_value["label"], description=value_value["description"], value=valuess))
                    else:
                        selectOption.append(nextcord.SelectOption(label=value_value["label"], value=valuess))
        selectOption.append(nextcord.SelectOption(label="Add payment",emoji=f"{config.EMOJI_ADD} ", value="add",))
        selectOption.append(nextcord.SelectOption(label="Go Back",emoji="🔙", value = "00",))
        
        embed=Embed(title="Embed stile editor payments", description=embedvalue, color=0x23929a)
        await interaction.message.edit(embed=embed,content=None, view=sview(self.bot,paymentssetup,interaction.user, 120,selectOption))
    
    async def subcategory_menu(self,interaction: Interaction, hcategory,scategory):
        test_value = db.subcategoriesdb.find_one({"guildid":interaction.guild_id,"headcategory":f"category{hcategory}","subcategory":f"subcategory{scategory}"})
    
        if test_value:
            embed=Embed(title=f"{test_value['label']} Setup", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
        else:
            embed=Embed(title=f"Category{scategory} Setup", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
        
        await interaction.message.edit(embed=embed, view=sview(self.bot,setupsubcategory2, interaction.user, 120,hcategory, scategory))
              
    
    
  
    



def setup(bot: Bot) -> None:
    bot.add_cog(setup_settings(bot))