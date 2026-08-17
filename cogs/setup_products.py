from itertools import permutations

import nextcord
from bson import ObjectId
from nextcord import Embed, Interaction
from nextcord.ext import commands
from nextcord.ext.commands import Bot
from pymongo import ReturnDocument

import config
from cogs.helpers import helpers
from utils import db, granks, is_int, nranks, sview


class productedit(nextcord.ui.Select):
    def __init__(self, bot:Bot, productid,hcategory, scategory=None):
        self.bot = bot 
        selectOption = [
            nextcord.SelectOption(label="Change Name", emoji="⚙️" ,value="1", ),
            nextcord.SelectOption(label="Change short description", emoji="🗂️" ,value="2", ),
            nextcord.SelectOption(label="change price", emoji="🗑️" ,value="3", ),
            
            nextcord.SelectOption(label="set pay options", emoji=config.EMOJI_PAYPAL ,value="4", ),
            nextcord.SelectOption(label="enable/disable", emoji="💡" ,value="5"),
            nextcord.SelectOption(label="delete", emoji="🗑️" ,value="6", ),
        ]
        self.productid =productid
        self.hcategory = hcategory
        self.scategory = scategory
        super().__init__(placeholder="select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0]
        productid =self.productid
        hcategory = self.hcategory
        scategory =self.scategory
        
            

        
        
        
            
        if int(value) == 1:
            embed=Embed(title="What name for product do you wanna use?", description="Just send in the Chat product name", color=0x23929a)
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
                product_name = text.content
                
                                
                db.productsdb.update_one({"guildid":interaction.guild_id,  "headcategory": f"category{hcategory}", "_id":productid}, {"$set":{"label":product_name}})              
                
                await interaction.send(f"**{config.EMOJI_YES}  Successfuly changed product name!**")
        elif int(value) == 2:
            pass
        elif int(value) == 3:
            embed=Embed(title="What price for product do you wanna use?", description="**Just send in the Chat product price without `€` just number(example: `5.50`)**", color=0x23929a)
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
                product_price = text.content
                if product_price.isdigit():
                    embed=Embed(title="ERROR | price isnt numeric", description="Cancelled the Operation!", color=0xff0000)
                    if interaction.guild is not None or interaction.guild.icon.url is not None:
                        embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                        
                    await interaction.send(embed=embed)
                else:
                    await interaction.send("Changed the price")
        elif int(value) == 4:
            
            paymethods = db.paymentsdb.find({"guildid":interaction.guild_id})
            product = db.productsdb.find_one({"guildid":interaction.guild_id, "_id":ObjectId(productid)})
            p_paymethods = product["payments"]
            selectOption = []
            embedvalue = ""
            count = 0
            for  value_value in paymethods:
                value_id = str(value_value["_id"])
                labe = value_value['label']
                emoji = value_value["emoji"]
                print(value_id)
                print(f"{value_id}")
                count = count + 1
                if value_id in p_paymethods:
                    if  emoji:
                        
                        if "description" in value_value and not "0" == value_value["description"]:
                            selectOption.append(nextcord.SelectOption(label=value_value['label'], description=value_value["description"],emoji=emoji, value=f"{value_id}"))
                            
                        else:
                            selectOption.append(nextcord.SelectOption(label=value_value['label'],emoji=emoji, value=f"{value_id}"))
                        embedvalue = embedvalue + f"{emoji}・{labe}・Enabled{config.EMOJI_YES}\n\n"
                        
                    else:
                        if "description" in value_value and not "0" == value_value["description"]:
                            selectOption.append(nextcord.SelectOption(label=value_value['label'], description=value_value["description"], value=f"{value_id}"))
                        else:
                            selectOption.append(nextcord.SelectOption(label=value_value['label'], value=f"{value_id}"))
                else:
                    if  emoji:
                        
                        if "description" in value_value and not "0" == value_value["description"]:
                            selectOption.append(nextcord.SelectOption(label=value_value['label'], description=value_value["description"],emoji=emoji, value=f"{value_id}"))
                            
                        else:
                            selectOption.append(nextcord.SelectOption(label=value_value['label'],emoji=emoji, value=f"{value_id}"))
                        embedvalue = embedvalue + f"{emoji}・{labe}・Disabled{config.EMOJI_NO}\n\n"
                        
                    else:
                        if "description" in value_value and not "0" == value_value["description"]:
                            selectOption.append(nextcord.SelectOption(label=value_value['label'], description=value_value["description"], value=f"{value_id}"))
                        else:
                            selectOption.append(nextcord.SelectOption(label=value_value['label'], value=f"{value_id}"))
                    
                
            embed=Embed(title="Enable/dissable specific pay option/s", description=f"**Select what you need in the `Selection` down Below!** \n\n{embedvalue}", color=0xfffff0)
            if count != 0:
                selectOption.append(nextcord.SelectOption(label="Clear",emoji="🗑️", value="Clear"))    


            await interaction.send(embed=embed, view=sview(self.bot,payoptionedit, interaction.user,120,selectOption, count, productid,hcategory,scategory)) 
        elif int(value) == 6:
            
            product = db.productsdb.find_one_and_delete({ "_id":ObjectId(productid)})
            await interaction.send(f" product {product['label']} (`{product['_id']}`) has been deleted{config.EMOJI_YES}! ")
            
        elif int(value) == 5:
            productsdbs = db.productsdb.find_one({ "_id":ObjectId(productid)})
            
            
            
            
            if productsdbs["enabled"]:
                
                await interaction.send(f"  category {productsdbs['label']} is now Disabled{config.EMOJI_NO}! ")
            else:
                await interaction.send(f" category {productsdbs['label']} is now Enabled{config.EMOJI_YES}! ")
                
            db.productsdb.update_one({"_id":ObjectId(productid)}, {"$set":{"enabled":(not productsdbs["enabled"] )}})


class payoptionedit(nextcord.ui.Select):
    def __init__(self,bot:Bot,selectOption, count, productid,hcategory,scategory= None):
        self.bot = bot 
        
        super().__init__(placeholder="select:", min_values=1, max_values=count, options=selectOption)
        self.hcategory =hcategory
        self.scategory = scategory
        self.productid = productid
    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0]
        hcategory = self.hcategory
        scategory = self.scategory
        productid = self.productid
        print(value)
        payments = []
        
        
            
            
        for valuedb in self.values:
            
            
            
            
            
            if not valuedb == "Clear":
                
                payments.append(valuedb)
                print(payments)
        product = db.productsdb.find_one_and_update({"guildid":interaction.guild_id,  "_id":ObjectId(productid)}, {"$set":{"payments":payments}},return_document=ReturnDocument.AFTER)
        
        p_paymethods = product["payments"]
        selectOption = []
        embedvalue = ""
        count = 0
        paymethods = db.paymentsdb.find({"guildid":interaction.guild_id})
        for  value_value in paymethods:
            value_id = str(value_value["_id"])
            labe = value_value['label']
            emoji = value_value["emoji"]
            print(value_id)
            
            count = count + 1
            if value_id in p_paymethods:
                if  emoji:
                    
                    if "description" in value_value and not "0" == value_value["description"]:
                        selectOption.append(nextcord.SelectOption(label=value_value['label'], description=value_value["description"],emoji=emoji, value=f"{value_id}"))
                        
                    else:
                        selectOption.append(nextcord.SelectOption(label=value_value['label'],emoji=emoji, value=f"{value_id}"))
                    embedvalue = embedvalue + f"{emoji}・{labe}・Enabled{config.EMOJI_YES}\n\n"
                    
                else:
                    if "description" in value_value and not "0" == value_value["description"]:
                        selectOption.append(nextcord.SelectOption(label=value_value['label'], description=value_value["description"], value=f"{value_id}"))
                    else:
                        selectOption.append(nextcord.SelectOption(label=value_value['label'], value=f"{value_id}"))
            else:
                if  emoji:
                    
                    if "description" in value_value and not "0" == value_value["description"]:
                        selectOption.append(nextcord.SelectOption(label=value_value['label'], description=value_value["description"],emoji=emoji, value=f"{value_id}"))
                        
                    else:
                        selectOption.append(nextcord.SelectOption(label=value_value['label'],emoji=emoji, value=f"{value_id}"))
                    embedvalue = embedvalue + f"{emoji}・{labe}・Disabled{config.EMOJI_NO}\n\n"
                    
                else:
                    if "description" in value_value and not "0" == value_value["description"]:
                        selectOption.append(nextcord.SelectOption(label=value_value['label'], description=value_value["description"], value=f"{value_id}"))
                    else:
                        selectOption.append(nextcord.SelectOption(label=value_value['label'], value=f"{value_id}"))
                
            
        embed=Embed(title="Enable/dissable specific pay option/s", description=f"**Select what you need in the `Selection` down Below!** \n\n{embedvalue}", color=0xfffff0)
        if count != 0:
            selectOption.append(nextcord.SelectOption(label="Clear",emoji="🗑️", value="Clear"))    


        await interaction.message.edit(embed=embed, view=sview(self.bot,payoptionedit, interaction.user,120,selectOption, count, productid,hcategory,scategory)) 

class ProductVersion(nextcord.ui.Select):
    def __init__(self, bot ,hcategory,scategory,types,typeid = None ,typeid2 = None ):
        self.bot = bot
        self.hcategory = hcategory
        self.scategory =scategory
        self.types = types
        self.typeid = typeid
        self.typeid2 = typeid2

        options = [
            nextcord.SelectOption(label="Fixed Price", emoji="🔢", value="1"),
            nextcord.SelectOption(label="Variable Price",  emoji="📈", value="2")
            ]

        super().__init__(placeholder="select price type ...", min_values=1, max_values=1, options=options)

    
    async def callback(self, interaction: nextcord.Interaction):
        value = self.values[0]
        
        hcategory = self.hcategory
        scategory = self.scategory
        types = self.types
        typeid =self.typeid
        if value == "1":
            await interaction.response.send_modal(cateproducts_qestions(self.bot,hcategory,scategory,types,typeid,self.typeid2))
        else:
            await interaction.response.send_modal(Variable_price_q(self.bot,hcategory,scategory,types,typeid,self.typeid2))
            
            
class Variable_price_q(nextcord.ui.Modal):
    def __init__(self, bot:Bot ,hcategory, scategory,types, typeid,typeid2):
        
        super().__init__(
            "Variable Price",
            timeout=2 * 60,  # 5 minutes
        )
        self.typeid2 =typeid2
        self.hcategory = hcategory 
        self.scategory = scategory
        self.types = types
        self.typeid =typeid
        self.variable_price = nextcord.ui.TextInput(
            label="What price u want to use? x = amount by user",
            placeholder="e.g. (x*1.5)*0.015",
            required=True,
            
            custom_id="Variable_price_q:variable_price",
            
        )
        self.add_item(self.variable_price)
        self.question = nextcord.ui.TextInput(
            label="Set Question for customer.",
            placeholder="e.g. How much comments do you want?",
            required=True,
            style=nextcord.TextInputStyle.paragraph,
            custom_id="Variable_price_q:question",
            
        )
        self.bot =bot
        self.add_item(self.question)
        
        

    async def callback(self, interaction: nextcord.Interaction) -> None:
        
        variable_price = str(self.variable_price.value)
        
        question = str(self.question.value)
        hcategory = self.hcategory
        scategory = self.scategory
        types =self.types
        typeid =self.typeid
        await interaction.send("Press button to continue",view=continue_button(self.bot,hcategory,scategory,types,typeid,self.typeid2,variable_price,question))
        
        
        
class continue_button(nextcord.ui.View):
    def __init__(self,bot: Bot,hcategory,scategory,types,typeid,typeid2,variable_price,question):
        self.bot = bot
        super().__init__()
        self.hcategory = hcategory 
        self.scategory = scategory
        self.types = types
        self.typeid =typeid
        self.variable_price =variable_price 
        self.question =question
        self.typeid2 =typeid2
    
    @nextcord.ui.button(label="continue", style=nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):   
         
        await interaction.response.send_modal(cateproducts_qestions(self.bot,self.hcategory,self.scategory,self.types,self.typeid,self.typeid,self.variable_price,self.question))     
                    

                
class cateproducts_qestions(nextcord.ui.Modal):
        def __init__(self, bot:Bot, hcategory,scategory,types,typeid,typeid2,variable_price=None,question=None):
            self.bot = bot
            super().__init__(
                "Setup Questions",
                timeout=2 * 60,  # 5 minutes
            )
            self.hcategory = hcategory
            self.scategory = scategory
            self.types =types
            self.typeid = typeid
            self.variable_price = variable_price
            self.question =question
            self.typeid2 = typeid2
            self.name = nextcord.ui.TextInput(
                label="What name for product do you wanna use?",
                placeholder="e.g. 100 Commends , 20 games...",
                required=True,
                
                custom_id="cateproducts_qestions:title",
                
            )
            self.add_item(self.name)
            self.description = nextcord.ui.TextInput(
                label="What short description do you wanna use?",
                placeholder="e.g. 100 CS:GO Commends, 20 Steam games",
                required=False,
                
                custom_id="cateproducts_qestions:description",
            )
            self.add_item(self.description)
            if not variable_price:
                self.price = nextcord.ui.TextInput(
                    label="What price for product do you wanna use?  ",
                    placeholder="e.g. 5.50, 20.00 - with decimals!!",
                    required=True,
                    
                    custom_id="cateproducts_qestions:price",
                )
                self.add_item(self.price)
            else:
                self.price = None 
                
            
            if types == "commendbot" and variable_price is None:
                self.amount = nextcord.ui.TextInput(
                label="How many commends do you want gift?",
                placeholder="e.g. 150, 254,500 , 1000... only numbers! ",
                required=True,
                
                custom_id="cateproducts_qestions:amount",
                )
                self.add_item(self.amount)
            
            elif types == "tf2keys" and variable_price is None:
                self.amount = nextcord.ui.TextInput(
                label="How many tf2 keys do you want gift?",
                placeholder="e.g. 1, 2, 5, 10... only numbers! ",
                required=True,
                
                custom_id="cateproducts_qestions:amount",
                )
                self.add_item(self.amount)
                
            else:
                self.amount = None
            
                
            

        async def callback(self, interaction: nextcord.Interaction) -> None:
            await interaction.response.defer()
            if self.price:
                product_price = self.price.value
            else:
                product_price = None
            product_name = self.name.value
            hcategory = self.hcategory
            scategory = self.scategory
            types = self.types
            typeid = self.typeid 
            typeid2 = self.typeid2
            variable_price = self.variable_price
            question = self.question
            amountg = False
            amount = None
            if self.amount:
                
                testvalue  :bool  = is_int(self.amount.value)
                if testvalue:
                    amount = int(self.amount.value)
                    amountg = True
                else:
                    embed=Embed(title="ERROR | Commends amount is not numbers", description="Cancelled the Operation!", color=0xff0000)
                    if interaction.guild is not None or interaction.guild.icon.url is not None:
                        embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                    await interaction.send(embed=embed,view=retry_modal(self.bot,hcategory,scategory,types,typeid,typeid2,variable_price, question))
                    
            else:
                amountg = True
                
                    
                    
                    
            
            if amountg:
            
            
            
                if self.description.value:
                    product_description =self.description.value
                else:
                    product_description = "0"
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
                    await interaction.channel.send(embed=embed,view=retry_modal(self.bot,hcategory,scategory,types,typeid,typeid2,variable_price, question))
                else:
                    


                    
                    product_emoji = str(reaction)
                    testvalue = product_emoji.replace(">" , "").split(":")
                    if 2 in testvalue :
                        testvalue = int(testvalue[2])
                    
                    
                        emoji = self.bot.get_emoji(testvalue)
                    else:
                    
                        emoji = testvalue[0]
                    
                    if emoji is not None:
                        
                        if product_price and product_price.isdigit():
                            embed=Embed(title="ERROR | price isnt numeric", description="Cancelled the Operation!", color=0xff0000)
                            if interaction.guild is not None or interaction.guild.icon.url is not None:
                                embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                            
                            await interaction.channel.send(embed=embed,view=retry_modal(self.bot,hcategory,scategory,types,typeid,typeid2,variable_price, question))
                        else:
                        
                        
                                paymethod = db.paymentsdb.find({"guildid":interaction.guild_id})
                                selectOption = []
                                embedvalue = ""
                                count = 0
                                

                                for  value_value in paymethod:
                                    value_id = str(value_value["_id"])
                                    labe = value_value['label']
                                    emoji = value_value["emoji"]
                                    print(value_id)
                                    
                                    count = count + 1
                                    if  emoji:
                                        
                                        if "description" in value_value and not "0" == value_value["description"]:
                                            selectOption.append(nextcord.SelectOption(label=value_value['label'], description=value_value["description"],emoji=emoji, value=f"{value_id}"))
                                            
                                        else:
                                            selectOption.append(nextcord.SelectOption(label=value_value['label'],emoji=emoji, value=f"{value_id}"))
                                        embedvalue = embedvalue + f"{emoji}・{labe}\n\n"
                                        
                                    else:
                                        if "description" in value_value and not "0" == value_value["description"]:
                                            selectOption.append(nextcord.SelectOption(label=value_value['label'], description=value_value["description"], value=f"{value_id}"))
                                        else:
                                            selectOption.append(nextcord.SelectOption(label=value_value['label'], value=f"{value_id}"))
                                if count != 0:
                                    
                                    embed=Embed(title="Select Pay Methods what u want to use!", description=f"**Select what you need in the `Selection` down Below!** \n\n{embedvalue}", color=0xfffff0)
                                    await interaction.send(embed=embed, view=sview(self.bot,payoptionsadd,interaction.user,120,selectOption, count, product_name, product_description, product_emoji,product_price,hcategory,scategory,types,typeid,typeid2,variable_price, question,amount)) 
                                else:
                                    await interaction.send("Skipping step... - You dont have setup any Pay Methods")
                            
                                
                    else:
                                embed=Embed(title="ERROR | This emoji isnt on your server!", description="Cancelled the Operation!", color=0xff0000)
                                if interaction.guild is not None or interaction.guild.icon.url is not None:
                                    embed.set_footer(text=interaction.guild , icon_url=interaction.guild.icon.url)
                                await interaction.channel.send(embed=embed,view=retry_modal(self.bot,hcategory,scategory,types,typeid,typeid2,variable_price, question))

 
 
class payoptionsadd(nextcord.ui.Select):
    def __init__(self,bot:Bot,selectOption, count, product_name, product_description, product_emoji,product_price,hcategory,scategory,types,typeid,typeid2,variable_price,question,amount):
        self.bot = bot 
        self.product_name = product_name
        self.product_description = product_description
        self.product_emoji = product_emoji
        self.product_price = product_price
        self.hcategory = hcategory
        self.scategory = scategory
        self.types = types
        self.typeid = typeid 
        self.variable_price  = variable_price
        self.question =question
        self.amount = amount
        self.typeid2 = typeid2
        
        super().__init__(placeholder="select:", min_values=1, max_values=count, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):

        product_name = self.product_name
        product_description = self.product_description
        product_emoji = self.product_emoji
        product_price = self.product_price
        hcategory =self.hcategory
        scategory = self.scategory
        types = self.types 
        typeid = self.typeid
        variable_price = self.variable_price
        question =self.question
        typeid2 =self.typeid2
        if self.amount:
            numberq = is_int(self.amount)
            if numberq:
                amount =self.amount
            else:
                amount = 1
        

        payments = []
     
        for valuedb in self.values:
            
    
            if not valuedb == "Clear":
                
                payments.append(valuedb)
                print(payments)
        spcategory = db.headcategorysdb.find_one({"guildid":interaction.guild_id, "headcategory":f"category{hcategory}"})
        if spcategory:
            addlist = {"guildid":interaction.guild_id, "headcategory": f"category{hcategory}", "label":product_name, "emoji":product_emoji,"enabled":True, "payments":payments,"type":types,}
            if  "no" not in product_description or "0" not in product_description:
                addlist["description"] = product_description
            if scategory:
                addlist["subcategory"] = f"subcategory{scategory}"
            if typeid :
                addlist["typeid"] = typeid
            if typeid2 :
                addlist["typeid2"] = typeid2
            if self.amount :
                addlist["amount_thing"] = amount  
            if variable_price is None:
                addlist["fixed_price"] = product_price
            else:
                addlist["variable_price"] = variable_price
                addlist["question_price"] = question
            print(addlist)
            db.productsdb.insert_one(addlist)
            await interaction.send("We added product to database!")
                               
    
class retry_modal(nextcord.ui.View):
    def __init__(self, bot:Bot,hcategory,scategory,types,typeid,typeid2,fixed,question):
        super().__init__()
        self.bot = bot
        self.hcategory = hcategory
        self.scategory = scategory
        self.types =types
        self.typeid =typeid 
        self.typeid2 = typeid2
        self.fixed =fixed
        self.question =question

    
    @nextcord.ui.button(label='Retry', style=nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(cateproducts_qestions(self.bot,self.hcategory, self.scategory,self.types,self.typeid,self.typeid2,self.fixed,self.question))
                                        
     

class setup_products(commands.Cog):
    
    

    def __init__(self, bot: Bot) -> None:
        self.bot = bot 
    running = False      
    @nextcord.slash_command(name="rankbal",description="rankbal")
    async def rankbal_command(self,interaction: Interaction,):  
        
        if not setup_products.running:
            setup_products.running = True
            
            ls = ("``` \n"
                "  s1 = 1        gn1 = 7        mge = 13 \n"
                "  s2 = 2        gn2 = 8        dmg = 14 \n"
                "  s3 = 3        gn3 = 9        le = 15 \n"
                "  s4 = 4        gn4 = 10       lem = 16 \n"
                "  se = 5        mg1 = 11       smfc = 17 \n"
                "  sem = 6       mg2 = 12       ge = 18"
                "\n ```")
                
            
            await interaction.send(ls)
            msg :nextcord.Message =await helpers.waitforrespon(self,interaction.channel,interaction.user,"msg",300)
            if msg:
                ranks = msg.content.split("-")
                numranks = []
                for rank in ranks:
                    if rank in granks:
                        numranks.append(granks[rank])
                    else:
                        await interaction.channel.send(f"rank {rank} not existing!")
                        break
                if len(ranks) == 10:
                    await setup_products.syncranks(self,numranks,interaction)
                
                        
                                    
                            
                            
                            
                    
                        
                else:
                    await interaction.channel.send("not enought ranks")
                setup_products.running = False   
        else:
            await interaction.send("please wait eta 1-2min till this command ll be free")    


            
            
            
    async def syncranks(self,numranks:list,interaction:Interaction =None):
        
        if len(numranks) == 10:
            numranks.sort(reverse=True)
            ranksdb = db.ranksvrai.find_one({"head":numranks,"type":"mm"})
            if ranksdb:
                aname = "**ateam ranks:**  "
                bname = "**bteam ranks:**  "
                besta = ranksdb["a"]
                bestb = ranksdb["b"]
                for id,an in enumerate(besta):
                    aname += f" **{id}.** {nranks[an]}" 
                for id,bn in enumerate(bestb):
                    bname += f" **{id}.** {nranks[bn]}" 
                if interaction: 
                    await interaction.channel.send(f"from db {aname}\n{bname}\nasum: {sum(besta)} bsum: {sum(bestb)}")
                else:
                    print(f"from db {aname}\n{bname}\nasum: {sum(besta)} bsum: {sum(bestb)}")
            else:
                
                g,c =[],[]
                for v in numranks: 
                    if (len(g) + len(c)) == 10:
                        break
                    else:    
                        if v == 0:
                            if len(g) < len(c):
                                g.append(v)
                            else: 
                                c.append(v)
                            
                        else:
                            if sum(g)<sum(c):
                                g.append(v)
                            else: 
                                c.append(v)
                print(abs(sum(g) - sum(c)))    
                if not (abs(sum(g) - sum(c))) == 0:
                        
                        
                    besttech = 999999
                    if interaction: 
                        await interaction.channel.send("wait it can take 0-2min to check all rank variatios!")
                    
                    print("creating a combinations")
                    comblist = list(permutations(numranks))
                    print("created a combinations")
                    comblist = list(set(comblist))
                    print("deleted duplicates")
                    copunt = len(comblist)   
                    print(copunt)
                    
                        
                    version = "ai"    
                    for num,comb in enumerate(list(comblist)):  
                        
                            if num > 43830 and besttech <2:
                                if interaction: 
                                    await interaction.channel.send("notend")
                                break 
                            elif num > 1563094 and besttech <3:
                                if interaction: 
                                    await interaction.channel.send("notend")
                                break
                            print(f"{(num+1)}/{copunt}")
                            g,c=[],[]
                            for v in comb:
                                
                                if (len(g) + len(c)) == 10:
                                    break
                                else:    
                                    if v == 0:
                                        if len(g) < len(c):
                                            g.append(v)
                                        else: 
                                            c.append(v)
                                        
                                    else:
                                        if sum(g)<sum(c):
                                            g.append(v)
                                        else: 
                                            c.append(v)
                            
                            diff = abs(sum(g) - sum(c))
                            if diff < besttech:
                                
                                besttech = diff
                                besta = g
                                bestb = c
                                idin = (num+1)
                                if besttech == 0:
                                    break 
                    
                    
                            
                            
                else:
                    version = "fast"
                    idin = 0
                    copunt = 0
                    besta = g
                    bestb = c
                    
                        
                aname = "**ateam ranks:**  "
                bname = "**bteam ranks:**  "
                for id,an in enumerate(besta):
                    aname += f" **{id}.** {nranks[an]}" 
                for id,bn in enumerate(bestb):
                    bname += f" **{id}.** {nranks[bn]}" 
                if interaction: 
                    await interaction.channel.send(f"{idin}/{copunt} {aname}\n{bname}\nasum: {sum(besta)} bsum: {sum(bestb)}")
                
                if version != "slow":
                    db.ranksvrai.insert_one({"type":"mm","head":numranks,"a":besta,"b":bestb,"version":version,"offset":abs(sum(besta) - sum(bestb))})        
    

def setup(bot: Bot) -> None:
    bot.add_cog(setup_products(bot))