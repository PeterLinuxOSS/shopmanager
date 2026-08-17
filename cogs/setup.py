
import nextcord
from nextcord import Colour, Embed, Interaction, TextChannel, User
from nextcord.ext import commands
from nextcord.ext.commands import Bot

import config
from cogs.helpers import helpers
from cogs.setup_views import (
    cateproducts,
    keysdatabase,
    paymentssetup,
    presetup,
    presetup2,
    setup_view,
    setupcategory,
    setupstylehead,
    setupsubcategory2,
    subsetup,
)
from utils import can_dm_user, db, embeds, sview, timestamp


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
        keysdbs = await db.subkeys.find({"guildid":interaction.guild.id,"database":_id}).to_list(length=None)
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
        hlist =await hcategorys.to_list(length=None)
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
            products = await db.productsdb.find({"guildid":interaction.guild_id, "headcategory": f"category{hcategory}", "subcategory":f"subcategory{scategory}"}).to_list(length=None)
        else:
            products = await db.productsdb.find({"guildid":interaction.guild_id, "headcategory": f"category{hcategory}"}).to_list(length=None)
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
        event2 = await db.headcategorysdb.find_one({"guildid":interaction.guild_id , "headcategory":f"category{hcategory}"})
                        
        if event2 :
            if event2["run"] and "subcategory" in event2["run"]:
                embed=Embed(title="subCategory Setup 🗂️ ", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
                scategory = db.subcategoriesdb.find({"guildid":interaction.guild_id,"headcategory":f"category{hcategory}"})
                
                hlist =await scategory.to_list(length=None)
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
     
    
        test_value = await db.headcategorysdb.find_one({"guildid":interaction.guild_id,"headcategory":f"category{hcategory}"})
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
            
            async for  value_value in paymethods:
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
        test_value = await db.subcategoriesdb.find_one({"guildid":interaction.guild_id,"headcategory":f"category{hcategory}","subcategory":f"subcategory{scategory}"})
    
        if test_value:
            embed=Embed(title=f"{test_value['label']} Setup", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
        else:
            embed=Embed(title=f"Category{scategory} Setup", description="**Select what you need in the `Selection` down Below!**", color=0x23929a)
        
        await interaction.message.edit(embed=embed, view=sview(self.bot,setupsubcategory2, interaction.user, 120,hcategory, scategory))


def setup(bot: Bot) -> None:
    bot.add_cog(setup_settings(bot))
