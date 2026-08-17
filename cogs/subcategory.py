
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Bot

from cogs.order import order, products
from cogs.ticket import ticketcs
from utils import db, sview


class subcategory(nextcord.ui.Select):
    def __init__(self, bot:Bot,selectOption):
        self.bot = bot 
        
        
                  
            
            

            
        super().__init__(placeholder="Select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):

        guild = interaction.guild
        subid =self.values[0]
        
        
                
            
        
        channeldb = await db.ticketsdb.find_one({"channelid":interaction.channel_id})
        subhead =    channeldb["category"]
        
        print(subhead)
        print(self.values[0])
        labe = await db.subcategoriesdb.find_one({"guildid":interaction.guild_id, "headcategory":subhead, "subcategory":subid})
        print(labe)
        if "run" in labe:
            if labe["run"] == "products":
                
                productsdbs = db.productsdb.find({"guildid":interaction.guild_id, "headcategory":channeldb["category"], "subcategory":subid,"enabled":True})
                
                
                    
                if productsdbs:
                    
                    
                    selectOption = []
                    numbers = 0
                    stylesdb = await db.embedstylesdb.find_one({"guildid":interaction.guild_id, "type":"productsmenu","headcategory":channeldb["category"], "subcategory":subid})
                    if stylesdb :

                        
                        if "description" in stylesdb:
                            embedvalue = f"{stylesdb['description']}\n\n"
                        else:
                            embedvalue = ""

                        async for  value_value in productsdbs:
                                value_id = str(value_value["_id"])
                                print(value_id)
                                numbers = numbers + 1
                                
                                emoji =value_value["emoji"]

                                if "type" in value_value and "ranksmm" in value_value["type"]:
                                    labeandprice = f"{value_value['label']} starts at {value_value['ranks']['1']}"
                                elif "fixed_price" in value_value:
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
                        


                        
                        color = stylesdb["color"]
                        color = int(hex(color), 0)
                        embed=nextcord.Embed(title=stylesdb["title"], description=embedvalue,color=color)
                                
                        if "image" in stylesdb:
                            embed.set_image(url=stylesdb["image"])
                        if "icon" in stylesdb:
                            embed.set_thumbnail(url=stylesdb["icon"])
                        if "footer-text" in stylesdb:
                            embed.set_footer(text=stylesdb["footer-text"])
                        
                        
                        
                        if numbers == 1:
                            
                            await order.product_skipper(self,interaction, value_value,subid)
                        
                        else:
                            
                            await interaction.message.edit(embed=embed , view=sview(self.bot,products,interaction.user,None,selectOption,subid))
                        
                        
                    else:
                        await interaction.send("This server dont have setup product style!")
                else:
                    await interaction.send("This server dont have any products in this subcategory!")
                
            elif labe["run"] == "ticket":
                
                
                headdb = await db.headcategorysdb.find_one({"guildid":guild.id,"headcategory":channeldb["category"]})
                await ticketcs.ticket(self=self,headcategorydb=headdb,channel=interaction,subcategorydb=labe)
                
            else:
                print("errror")
        else:
            await interaction.send("This server dont have setup events for this subcategory")

            
            
    


                
                              
                

class subcategorycs(commands.Cog):
    
    

    def __init__(self, bot: Bot) -> None:
        self.bot = bot 
        
    pass
    
    

def setup(bot: Bot) -> None:
    bot.add_cog(subcategorycs(bot))