import datetime
from email import message

import nextcord
from bson import ObjectId
from nextcord import Colour, Embed, Interaction, Member, TextChannel, User
from nextcord.components import SelectOption
from nextcord.ext import commands
from nextcord.ext.commands import Bot
from pymongo import ReturnDocument
from steam import steamid
from termcolor import cprint

import config
from cogs.helpers import helpers, retry_button
from utils import (db, eranks, is_int, logo, rank_options, round_up, server_name,
                   sview, timestamp, tz)


class paypal_again(nextcord.ui.View):
    def __init__(self,bot:Bot,types,check,checkchannel,price,link):
        super().__init__()
        self.value = None
        self.bot = bot
        self.types = types
        self.check = check
        self.checkchannel = checkchannel
        self.price = price
        self.link =link
   
    @nextcord.ui.button(label="Again", style=nextcord.ButtonStyle.red)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        
        await order.processpaypalv(self,interaction.user, interaction.channel,self.types, self.check, self.checkchannel,self.link,interaction,self.price)
        
        

        
                
class payments(nextcord.ui.Select):
    def __init__(self,bot:Bot ,selectOption):
        self.bot = bot
        
                  
            
            

            
        super().__init__(placeholder="Select:", min_values=1, max_values=1, options=selectOption)

    async def callback(self, interaction: nextcord.Interaction):
        
        
        
        ticketdb = db.ticketsdb.find_one_and_update({"channelid":interaction.channel_id} ,[{"$set":{"payment":self.values[0],"legitstatus":"Ineligible","gifterid":config.OWNER_ID}}])
        if "type" in ticketdb and "ranksmm" == ticketdb["type"]:
            await order.selectrank(self,interaction)
            
            
        else:
            await order.paymentshort(self,interaction.channel, self.values[0],interaction.message)       



class currentrank(nextcord.ui.Select):
    def __init__(self,bot:Bot):
        self.bot = bot 
        options = rank_options()

        super().__init__(
            placeholder="Select your current rank",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: nextcord.Interaction):
        current_rank = int(self.values[0])
        tdb = db.ticketsdb.find_one_and_update({"channelid":interaction.channel_id} ,{"$set":{"currentrank":current_rank}})
        
        rankup = tdb["rankup"] if "rankup" in tdb else False 
        derank = tdb["derank"] if "derank" in tdb else False 
        if not derank and rankup:
            options = rank_options(i for i in range(1, 19) if i > current_rank)
        elif derank and not rankup:
            options = rank_options(i for i in range(1, 19) if i < current_rank)
        else:
            # Both set, or neither. The original had no else branch, so a ticket
            # with neither flag left `options` unbound and raised NameError on
            # the edit below; offering every rank is the permissive default.
            options = rank_options()

        embed = nextcord.Embed(title="Select your dream CS:GO rank", description="**Select your dream cs:go rank in the `Selection` down Below!**", color=Colour.blurple(), timestamp=timestamp,)
        await interaction.message.edit(embed=embed,view=sview(self.bot,dreamrank, interaction.user,120,options,))
        
        
class dreamrank(nextcord.ui.Select):
    def __init__(self,bot:Bot,options):
        self.bot = bot 
                    
                
                
            
            
        
        super().__init__(
            placeholder="Select your dream rank",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: nextcord.Interaction):        
        dream_rank = int(self.values[0])
        tdb = db.ticketsdb.find_one_and_update({"channelid":interaction.channel_id} ,{"$set":{"dreamrank":dream_rank}},return_document=ReturnDocument.AFTER)
        
        ranks :dict= tdb["ranks"]
        current_rank  = tdb["currentrank"]
        total_price = 0 
        for rank, price in ranks.items():
            if int(rank) > int(current_rank) and int(rank) <= int(dream_rank):
                total_price += price
                print(rank)
        db.ticketsdb.update_one({"channelid":interaction.channel_id} ,{"$set":{"productprice":total_price}})
        
        await order.paymentshort(self,interaction.channel, tdb["payment"],interaction.message)

  
class give_product(nextcord.ui.View):
    def __init__(self,bot:Bot):
        super().__init__()
        self.bot = bot 
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @nextcord.ui.button(label="Only for support!", style=nextcord.ButtonStyle.red)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):  
        
        if interaction.user.guild_permissions.manage_messages or interaction.user.guild_permissions.manage_channels or interaction.user.guild_permissions.administrator or interaction.user.guild_permissions.mute_members or interaction.user.id == self.bot.owner_id:
            self.stop()
            
            await interaction.send("  ", ephemeral=True)
            db.refreshview.delete_one({"channelid":interaction.channel_id, "msgid":interaction.message.id,"view":"give_product"})
            await order.delivery_product(self,interaction.channel)
            
            
        else:
            embed=nextcord.Embed(title=f"{config.EMOJI_NO} Missing Permissions", description="You need one of this Permissions:\n> `ADMINISTRATOR`\n> `MUTE_MEMBERS`\n> `MANAGE_CHANNELS`\n> `MANAGE_MESSAGES`", color=0xff0000)
            await interaction.send(embed=embed, ephemeral=True)
  
                
       
        
        
class dissableg(nextcord.ui.View):
    def __init__(self,item):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(item)
   
        
class closebutton(nextcord.ui.Button):
    def __init__(self, bot:Bot,):
        self.bot = bot
        

        super().__init__(
            label="Close ticket", style=nextcord.ButtonStyle.red
        )
        
    
    async def callback(self, interaction: nextcord.Interaction):    
        await helpers.close_ticket(self,interaction)
        
    
class ConfirmButton2(nextcord.ui.Button):
    def __init__(self, bot:Bot,value,label):
        self.bot = bot
        
        # Set the options that will be presented inside the dropdown
        

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(
            label=label, style=nextcord.ButtonStyle.green
        )
        self.value =value
        self.label = label
    
    async def callback(self, interaction: nextcord.Interaction):
        db.refreshview.delete_one({"channelid":interaction.channel_id,"code":"order.paymentshort"})
        await interaction.response.send_message('Confirming', ephemeral=True)
        value = self.value
        self.disabled = True
        await interaction.message.edit(view=dissableg(self))
        ticketdb = db.ticketsdb.find_one({"channelid":interaction.channel_id})
        price = ticketdb["productprice"]
        paypaldb = db.paymentsdb.find_one({"guildid":interaction.guild_id, "_id": ObjectId(self.value)})
        go = True
        if ticketdb["type"] == "tf2keys":
            gooddb = db.goodsdb.find_one({"guilds":interaction.guild.id, "type":"tf2keys"})
            onhold = gooddb["onhold"]
            if onhold <= 0:
                onhold = 0
                db.goodsdb.update_one({'_id': gooddb["_id"]}, {'$set': {'onhold': onhold}})
            
            
            if (gooddb["stock"] - onhold) >= int(ticketdb["amount_thing"]):
                db.goodsdb.update_one({'_id': gooddb["_id"]}, {'$inc': {'onhold': +int(ticketdb["amount_thing"])}})
            else:
                await interaction.channel.send(f"Sorry we currently have only {gooddb['stock']} tf2 keys")
                go = False
        elif ticketdb["type"] == "commendbot":
            gooddb = db.goodsdb.find_one({"guilds":interaction.guild.id, "type":"commendbot"})
                    
                        
                            
                
            
            
        if go:
            if self.value == "6294dccf41d666c356817e6b" or self.value == "66e6db57720f7c71bf87017d":
                
                
                
                
                # put here other code for start pay 
                embed=nextcord.Embed(title="Set type of verify your payment! ", color=nextcord.Color.blurple())
                await interaction.channel.send(embed=embed, view=sview(self.bot,paypalmenu,interaction.user,None,paypaldb["channelid"],paypaldb["link"]))
            elif self.value == "62f150757bd3e416dc2ca445": 
                
                heckcahnnel = self.bot.get_channel(paypaldb["channelid"])
                
                await interaction.channel.send("Please send link to your steam pofile from what u want to send trade")
                try:
                    text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == interaction.channel and  message.author == interaction.user , timeout=500)
                except Exception:
                    msg = await interaction.channel.send("timeout",view=sview(self.bot,ConfirmButton2,None,None,value,self.label))
                    db.refreshview.insert_one({"channelid":interaction.channel_id, "msgid":msg.id,"view":"ConfirmButton2view","values":{type(value):value, type(self.label):self.label}}) 
                else:
                    steamID64 = None
                    if len(text.content) == 17:
                        steamID64 = int(text.content)
                    elif "/id/" in text.content or "/profiles/"  in text.content:
                        try:    
                            urls = steamid.steam64_from_url(text.content, http_timeout=30)
                        except Exception:
                            
                            embed=nextcord.Embed(title="Timeout", description="We didnt get any respond ", color=0xe74c3c)
                            try:
                                ms: message.Message = await interaction.channel.send(content=" ",embed=embed,view=sview(self.bot,ConfirmButton2,None,None,value,self.label))
                            except Exception:
                                pass
                            else:
                                db.refreshview.insert_one({"channelid":interaction.channel_id, "msgid":ms.id,"view":"ConfirmButton2view","values":[value, self.label]}) 
                        else:
                            
                            if urls:

                                steamID64 = urls
                                
                            else:
                                
                                embed=nextcord.Embed(title="Unkow error", description="we cant verify if this is a steam link", color=0xe74c3c)
                                msg = await interaction.channel.send(content=" try again",embed=embed,view=sview(self.bot,ConfirmButton2,None,None,value,self.label))
                                db.refreshview.insert_one({"channelid":interaction.channel_id, "msgid":msg.id,"view":"ConfirmButton2view","values":[value, self.label]}) 
                    if steamID64 is not None:
                        embed=nextcord.Embed(color=Colour.blurple())
                        embed.set_author(name= server_name, url=logo, icon_url=logo)
                        embed.set_thumbnail(url=logo)
                        embed.add_field(name="**Steam Tradelink**", value=paypaldb["tradelink"], inline=False)
                        embed.set_footer(text= server_name)
                        await interaction.channel.send(embed=embed)
                        db.globalchecker.insert_one({"chchannelid":heckcahnnel.id,"channelid":interaction.channel.id, "template":"steam","appid":730,"datetime":datetime.datetime.now(tz=tz),"paymentid":ObjectId(self.value),"steamid":steamID64,"price":float(price)})
                    
                    
                    
                    
                    
            else:
                paydb = db.paymentsdb.find_one({"guildid":interaction.guild_id, "_id":ObjectId(self.value)})
                
                await interaction.channel.send(paydb["text"])
                



class products(nextcord.ui.Select):
    def __init__(self, bot:Bot,selectOption, subid=None):
        self.subid = subid
        self.bot = bot
                  
            
            

            
        super().__init__(placeholder="Select:", min_values=1, max_values=1, options=selectOption)
        
    async def callback(self, interaction: nextcord.Interaction):

        
        
        
        
        product = db.productsdb.find_one({"guildid":interaction.guild_id,  "_id":ObjectId(self.values[0])})
        await order.product_skipper(self,interaction, product,self.subid)

                
class price_qestion(nextcord.ui.Modal):
    def __init__(self, bot:Bot,question):
        self.bot = bot
        super().__init__(
            "Question",
            timeout=None 
        )

        self.name = nextcord.ui.TextInput(
            label=question,
            min_length=1,
            placeholder="only numbers!",
            max_length=100,
            required=True
        )
        self.add_item(self.name)

        
        
        self.value = None

    async def callback(self, interaction: nextcord.Interaction) -> None:
        self.value = self.name.value
        
        await interaction.response.defer()
        self.stop()                                   



class paypalmenu(nextcord.ui.Select):
    def __init__(self,bot:Bot,checkchannel,link):
        self.checkchannel =checkchannel
        self.link = link
        self.bot = bot
        options = [
            nextcord.SelectOption(label="Paypal Mail Address", emoji="🟨",value=0),
            nextcord.SelectOption(label="PayPal User ID", emoji="🟥",value=1),
            nextcord.SelectOption(label="PayPal Lastname", emoji="🟩",value=2),
            nextcord.SelectOption(label="PayPal payment text(note)", emoji="🟦", value=3),
            
        ]

        super().__init__(
            placeholder="Choose verify method...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: nextcord.Interaction):
        self.disabled = True
        
        value = int(self.values[0])
        link = self.link
        channel =interaction.channel
        if value == 0:
            modal = pmodal(self.bot,"Your PayPal Mail Address", "yourmail@gmail.com","mail",self.checkchannel,link)
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value is None:
                print("timeoutttttttttt")
            else:
                print("here dissable it ")
                self.disabled = True
                await interaction.message.edit(view=dissableg(self))
        
        elif value == 1:
            modal =pmodal(self.bot,"Your PayPal Merchant ID", "paypal.com/myaccount/settings","id",self.checkchannel,link)
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value is None:
                print("timeoutttttttttt")
            else:
                print("here dissable it ")
                self.disabled = True
                await interaction.message.edit(view=dissableg(self))
        elif value == 2:
            modal = pmodal(self.bot,"Your PayPal Last Name", "paypal.com/myaccount/settings","lastname",self.checkchannel,link)
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value is None:
                print("timeoutttttttttt")
            else:
                print("here dissable it ")
                self.disabled = True
                await interaction.message.edit(view=dissableg(self))
        elif value == 3:
            self.disabled = True
            await interaction.message.edit(view=dissableg(self))
            embed=nextcord.Embed(title="Secret Code", description="Please type your secret code to note without any space please", color=0xff0000)
            embed.set_image(url=config.IMAGE_SETUP_TUTORIAL)
            await interaction.response.send_message(embed=embed)
            code = str(channel.id) 
            await channel.send(f"```js\n Your secret code is: {code} \n```")

            await order.processpaypalv(self,interaction.user, interaction.channel,"note", code, self.checkchannel,link)           
            
class pmodal(nextcord.ui.Modal):
    def __init__(self,bot:Bot,label,placeholder,types,checkchannel,link):
        self.bot = bot
        super().__init__(
            title="Verify",
            
            custom_id="persistent_modal:Questions",
            timeout=None,
            
        )
        self.value =None
        self.qmodal = nextcord.ui.TextInput(
            label=label,
            placeholder=placeholder,
            required=True,
            style=nextcord.TextInputStyle.short,
        )
        self.add_item(self.qmodal)
        self.checkchannel = checkchannel
        self.types = types
        self.link = link
        
        
        

    async def callback(self, interaction: nextcord.Interaction):
        self.value =True
        self.stop()
        await order.processpaypalv(self,interaction.user, interaction.channel,self.types, self.qmodal.value, self.checkchannel,self.link,interaction)      
                       
class change_smth(nextcord.ui.Select):
    def __init__(self, bot:Bot,options, value2):
        self.bot = bot
      
        super().__init__(
            placeholder="Select What u want change:",
            min_values=1,
            max_values=1,
            options=options,
        )
        self.value2 = value2
        

    async def callback(self, interaction: nextcord.Interaction):
        next = False
        payid = self.value2
        
        channeldb = db.ticketsdb.find_one({"channelid":interaction.channel_id})
        
        print("here s")
        print(self.values[0])
        if int(self.values[0]) == 1:
            
            product =db.productsdb.find_one({"_id":ObjectId(channeldb["product_id"])})
            question = product["question_price"]
            view = price_qestion(self.bot,question)
            
            
            await interaction.response.send_modal(view)
            await view.wait()
            if view.value is None:
                await interaction.send("Try again ",ephemeral=True)
                
            elif view.value:
                x = view.value
                print(x)
                fixed_price : str = product["variable_price"] 
                fixed_price = fixed_price.replace("x", x)
                try:
                    fixed_price = eval(fixed_price)
                except Exception:
                    await interaction.send("Error is not number!")
                    
                fixed_price = round_up(float(fixed_price))
                print(fixed_price)
                db.ticketsdb.update_one({"channelid":interaction.channel_id} ,[{"$set":{"productprice":fixed_price,"amount_thing":x}}])
                channeldb = db.ticketsdb.find_one({"channelid":interaction.channel_id})
            else:
                await interaction.send("Try again ",ephemeral=True)
        elif int(self.values[0]) == 5:
            next = True
            await order.selectrank(self,interaction)
            
        elif int(self.values[0]) == 2: #change payment method
            product =db.productsdb.find_one({"_id":ObjectId(channeldb["product_id"])})
            
            next = True
            
            await order.send_pay_methods(self,channeldb.get("subchannelid"),product,interaction)
        if not next:        
            await order.paymentshort(self,interaction.channel,payid,interaction.message)
   
class change_smthView(nextcord.ui.View):
    def __init__(self, bot:Bot, value,value2,label):
        
        super().__init__(timeout=None)
        

        # Adds the dropdown to our view object.
        self.add_item(change_smth(bot,value,value2))
        
        self.add_item(ConfirmButton2(bot,value2,label))
        self.add_item(closebutton(bot))
    async def on_timeout(self):
        print("change_smthView-end")
        self.clear_items()         
         

            
class order(commands.Cog):
    
    

    def __init__(self, bot: Bot) -> None:
        self.bot = bot 
        
        
        
        
        
    async def processpaypalv(self,user:User | Member, realchannel:TextChannel, types, check,checkcahnnel,link,interaction:nextcord.Interaction = None,needprice =None):
        embed=nextcord.Embed(color=nextcord.Color.blurple())
        embed.set_author(name= server_name, url=logo, icon_url=logo)
        embed.set_thumbnail(url=logo)
        embed.add_field(name=f"Hey {user.name} Send money as **Friends & Family** only or will cancel your order, no refund!!",value='If you dont have this option or dont see this option, please do not send **money** and ping the admins and wait for help!!!\n**Please set in order note text: for friend**',inline=False)
        embed.add_field(name="Tutorial " ,value=" https://youtube.com/watch?v=6M20RgpIgyI&feature=shares",inline=False)
        embed.set_image(url=config.IMAGE_PRODUCT_TUTORIAL)
        
        embed.add_field(name="**Server´s PayPal**", value=link, inline=False)
        if interaction:
            await interaction.send(embed=embed)
        else:
            await realchannel.send(embed=embed)
        tdb = db.ticketsdb.find_one({"channelid":realchannel.id})
        if needprice:
            price = needprice
        else:
            price = tdb["productprice"]
        db.globalchecker.insert_one({"chchannelid":checkcahnnel,"channelid":realchannel.id, "template":"paypalv","datetime":datetime.datetime.now(tz=tz),"paymentid":ObjectId(tdb["payment"]),"price":float(price), "type":types,"check":check,"link":link})
        
        
    async def paymentshort(self,channel:nextcord.TextChannel,payid,msg: nextcord.Message,refresh: nextcord.Message=None):
    
        channeldb = db.ticketsdb.find_one({"channelid":channel.id})
        if not channeldb:
            await channel.delete()
            return
        embed=Embed(title="Ticket- Informations", color=0x75d373)
        if channeldb and "category" not in channeldb:
            raise BaseException(f"error-cat - {channeldb}")
        
        headdb = db.headcategorysdb.find_one({"guildid":channel.guild.id,"headcategory":channeldb["category"]})
        
        embed.add_field(name="Category:", value=f'{headdb["emoji"]}・{headdb["label"]}', inline=False)
        if "subcategory" in channeldb:
            db.subdb = db.subcategoriesdb.find_one({"guildid":channel.guild.id, "headcategory":channeldb["category"], "subcategory":channeldb["subcategory"]})
            embed.add_field(name="subCategory:", value=f'{db.subdb["emoji"]}・{db.subdb["label"]}', inline=False)
        
        paydb = db.paymentsdb.find_one({"guildid":channel.guild.id, "_id":ObjectId(payid)})
        
        embed.add_field(name="Product name:", value=channeldb["productname"], inline=False)
        embed.add_field(name="Payment", value=paydb["label"], inline=False)
        selectOption =[]
        if channeldb["variable"]:
            embed.add_field(name="amount", value=channeldb["amount_thing"], inline=False)
            selectOption.append(nextcord.SelectOption( label="Change amount", emoji="🟩" ,value=1))
        if "fees" in channeldb:
            
            embed.add_field(name="Product Price", value=f"{channeldb['productprice']+channeldb['fees']}€", inline=True)
            embed.add_field(name="Aditional Fees for Payment", value=f"{channeldb['fees']}€", inline=True)
        else:
            embed.add_field(name="Product Price", value=f"{channeldb['productprice']}€", inline=False)
        selectOption.append(nextcord.SelectOption(label="Change Payment method", emoji="🟥",value=2))
        
        if "question1" in channeldb:
            embed.add_field(name=f"Question-1: {channeldb['question1-q']}", value=channeldb['question1-r'], inline=False)
            selectOption.append(nextcord.SelectOption(label="Change Question-1 answer", emoji="🟥",value=3))
        if "question2" in channeldb:
            embed.add_field(name=f"Question-2: {channeldb['question2-q']}", value=channeldb['question2-r'], inline=False)
            selectOption.append(nextcord.SelectOption(label="Change Question-2 answer", emoji="🟥",value=4))
        if "image_url" in channeldb:
            embed.set_image(url=channeldb["image_url"])
        if "currentrank" in channeldb and "dreamrank" in channeldb:
            selectOption.append(nextcord.SelectOption(label="Change rank/s", emoji="🟥",value=5))
            
            embed.add_field(name="Current rank", value=f"{eranks[channeldb['currentrank']]}", inline=False)
            embed.add_field(name="Dream rank", value=f"{eranks[channeldb['dreamrank']]}", inline=False)
            

        view = change_smthView(self.bot,selectOption, payid,"Confirm") 
        await msg.edit(embed=embed, view=view)
        if not db.refreshview.find_one({"channelid":channel.id,"code":"order.paymentshort","msgid":msg.id,}):
            
            db.refreshview.insert_one({"channelid":channel.id,"msgid":msg.id,"values":[payid],"code":"order.paymentshort"}) 
        
    async def selectrank(self,interaction:Interaction):
        embed = nextcord.Embed(title="Select your current CS:GO rank", description="**Select your current cs:go rank in the `Selection` down Below!**", color=Colour.blurple(), timestamp=timestamp,)
        await interaction.message.edit(embed=embed,view=sview(self.bot,currentrank, interaction.user,120))
    
    async def delivery_product(self,channel:nextcord.TextChannel):
        print(f"delivery_product for {channel.id}")
        
        ivalue = db.ticketsdb.find_one({"channelid":channel.id})
        
        if "commendbot" == ivalue["type"]:
            
            
            amount = int(ivalue["amount_thing"])
            gooddb = db.goodsdb.find_one({"guilds":channel.guild.id, "type":"commendbot"})
            
            channelds = self.bot.get_channel(config.ORDER_LOG_CHANNEL_ID)
            await channelds.send(f"c!transferbot {gooddb['userid']} {amount} {ivalue['userid']} {gooddb['slots']}")
            
            try:
                msg : nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == channelds and message.author.id != self.bot.user.id , timeout=30)
            except Exception:
                embed = nextcord.Embed(title="Timeout", description="Please ping anybody from support because commendbot is off and i can give u balance!", color=Colour.dark_blue(), timestamp=timestamp,)
                await channel.send(embed=embed)

            else:
                if "gifted" in msg.content:
                
                    embed = nextcord.Embed(title="success", description=f"Your {amount} commends has been gifted!(use /balance in this channel or in <@1134090688200462396> dms)", color=Colour.brand_green(), timestamp=timestamp,)
                    await channel.send(embed=embed)
                elif "blacklist-g" in msg.content: 
                    embed = nextcord.Embed(title="Blacklist Error", description=f"Gifter <@{gooddb['userid']}> is blacklisted in commendbot!", color=Colour.dark_blue(), timestamp=timestamp,)
                    await channel.send(embed=embed) 
                    
                elif "blacklist-c" in msg.content: 
                    embed = nextcord.Embed(title="Blacklist Error", description=f"<@{ivalue['userid']}> You are blacklisted in commendbot!", color=Colour.dark_blue(), timestamp=timestamp,)
                    await channel.send(embed=embed)
                
                else:
                    embed = nextcord.Embed(title="Error", description=f"Please ping anybody from support because commendbot is off and i can give u balance!(Error: {msg.content})", color=Colour.dark_blue(), timestamp=timestamp,)
                    await channel.send(embed=embed)
    
                
        elif "tf2keys" == ivalue["type"]:
            amount = int(ivalue["amount_thing"])
            gooddb = db.goodsdb.find_one({"guilds":channel.guild.id, "type":"tf2keys"})
            embed = nextcord.Embed(title="Please send in to chat your tradelink!", description="You can find your tradelink here: https://steamcommunity.com/sharedfiles/filedetails/?id=354215515", color=Colour.green(), timestamp=timestamp,)
            await channel.send(embed=embed)
            user = self.bot.get_user(ivalue["userid"])
            msg =await helpers.waitforrespon(self,channel, user,"msg",180)
            if msg:
                checkchannel = self.bot.get_channel(gooddb["channelid"])
                await checkchannel.send(f"s!send {amount} {msg.content}")
                db.goodsdb.update_one({'_id': gooddb["_id"]}, {'$inc': {'onhold': -amount}})
                db.ticketsdb.update_one({'_id': ivalue["_id"]}, {'$set': {'status': "finished"}})
                try:
                    msgs : nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == checkchannel and "send-" in message.content, timeout=20)
                except Exception:
                    await channel.send("Error bot not responding!")
                else:
                    if "sent" in msgs.content:
                        await channel.send("we send to you tf2 keys ")
                    else:
                        await channel.send("Error please wait for admin")
        elif "keys" == ivalue["type"]:
            key = db.keysdb.find_one_and_delete({"database":ObjectId(ivalue["typeid"]),"subdatabase":ObjectId(ivalue["typeid2"])})
            keysdbs = db.subkeys.find_one({"database":ObjectId(ivalue["typeid"]),"_id":ObjectId(ivalue["typeid2"])})
            embed = nextcord.Embed(title="Instructions", description=keysdbs["instructions"], color=Colour.gold(), timestamp=timestamp,)
            embed.add_field(name="Your Key", value=f"||{key['key']}||", inline=False)
            await channel.send(embed=embed)
            
            
                
        
                
        else:

            pass    
        
        
    async def product_skipper(self,interaction: nextcord.Interaction , product,schannel=None):

        print("lololslosos")
        cprint(product)
        
        if "payments" not in product:
            
            
            await interaction.message.edit(content="This server dont have setup payments for specific product!")    
            return
       
        paymentss: list = product["payments"]
        
        if  "fixed_price" in product:
            fixed_price = product["fixed_price"]
        
            
        else :
            
            question = product["question_price"]
            view = price_qestion(self.bot,question)
            await interaction.message.edit(f"Skipping the menu because in menu was only 1 product: {product['label']}",view=retry_button(self.bot, view,product,paymentss,schannel),embed=None)
            
            
            await interaction.response.send_modal(view)
            await view.wait()
            if view.value is None:
                await interaction.send("Try again ")
                return
            elif view.value:
                
                x = view.value
                isint = is_int(x)
                if isint:
                    x = int(x)
                    if x <= 0:
                        x = 1
                    
                    fixed_price : str = product["variable_price"] 
                    fixed_price = fixed_price.replace("x", str(x))
                    try:
                        fixed_price = eval(fixed_price)
                    except Exception:
                        await interaction.send(f"Error variable_price is not number!({fixed_price})", view=None)
                        return
                    fixed_price = round_up(fixed_price)
                    print(fixed_price)
                    
                    
                    
                        
                    
                
                    
                    
                else:
                    await interaction.send("This isnt a number ",retry_button(self.bot,view,product,paymentss,schannel))
                    
                
            else:
                await interaction.send("Try again ",view= retry_button(self.bot,product,paymentss,schannel))
                return
            
        adds = {"product_id":product["_id"], "productprice":fixed_price,"productname":product["label"],"type":product["type"],}
        if schannel:
            adds["subchannelid"] = schannel
        if "type" in product and "ranksmm" in product["type"]:
            adds["variable"] = False
            adds["ranks"] = product["ranks"]
            
            adds["rankup"] = product["rankup"]
            
            adds["derank"] = product["derank"]
            
            adds["productprice"] = 0
            
            
            
        else:
                
            if "amount_thing" in product:
                adds["amount_thing"] = product["amount_thing"]
            if "fixed_price" in product:
                adds["variable"] = False
            else:
                adds["variable"] = True
                adds["amount_thing"] = x
            if "typeid" in product:
                adds["typeid"] = product["typeid"]
            if "typeid2" in product:
                adds["typeid2"] = product["typeid2"]

                
        
        
        db.ticketsdb.update_one({"channelid":interaction.channel.id} ,{'$set': adds})        
            
    
        await order.send_pay_methods(self,schannel,product,interaction)
        

    

        
    async def send_pay_methods(self,schannel:str,product:dict,interaction:Interaction,paymentss:list=None):
        if not paymentss:
            paymentss = product["payments"]
        guild = interaction.guild
        selectOption = []
        numbers = 0
        
        if schannel:
            
            stylesdb = db.embedstylesdb.find_one({"guildid":guild.id, "type":"payments","headcategory":product["headcategory"],"subcategory":schannel})
        else:
            stylesdb = db.embedstylesdb.find_one({"guildid":guild.id, "type":"payments","headcategory":product["headcategory"],})
        if stylesdb:
            
            
            if "description" in stylesdb:
                embedvalue = f"{stylesdb['description']}\n\n"
            else:
                embedvalue = ""
            
            
            
            for payment_id   in paymentss:
                paydb = db.paymentsdb.find_one({"guildid":guild.id, "_id":ObjectId(payment_id)})
                if paydb:
                
                    numbers = numbers + 1
                    if "description" in paydb and not "0" == paydb["description"] or "no" == paydb["description"]:

                        selectOption.append(nextcord.SelectOption(label=paydb["label"], emoji=paydb["emoji"], value=f"{payment_id}",description=paydb["description"]))
                    else:
                        selectOption.append(nextcord.SelectOption(label=paydb["label"], emoji=paydb["emoji"], value=f"{payment_id}"))
                    embedvalue = embedvalue + f"{paydb['emoji']}・{paydb['label']}\n\n"
                else:
                    plist = paymentss.copy()
                    plist.remove(payment_id)
                    db.productsdb.update_one({"_id":product["_id"]}, {"$set":{"payments":plist}})
                    
                color = stylesdb["color"]
            color = int(hex(color), 0)  
            embed=nextcord.Embed(title=stylesdb["title"], description=embedvalue,color=color)

                        
            if "image" in stylesdb:
                embed.set_image(url=stylesdb["image"])
            if "icon" in stylesdb:
                embed.set_thumbnail(url=stylesdb["icon"])
            if "footer-text" in stylesdb:
                embed.set_footer(text=stylesdb["footer-text"])
            
            
            
            await interaction.message.edit(content=None,embed=embed , view=sview(self.bot,payments, interaction.user,None,selectOption))
        else:
            await interaction.message.edit(content="This server dont have setup payments style for specific product!")
        

def setup(bot: Bot) -> None:
    bot.add_cog(order(bot))