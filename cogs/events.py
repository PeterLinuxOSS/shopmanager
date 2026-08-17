import asyncio
import config
import datetime

import nextcord
import pymongo
import unidecode
from bson import ObjectId
from nextcord import Colour, Guild
from nextcord.ext import commands
from nextcord.ext.commands import Bot

from cogs.bot_tasks import bot_tasks
from cogs.headcategory import headcategorycs
from cogs.order import ConfirmButton2, give_product, order, paypal_again

# (nothing needed from cogs.helpers)
# (nothing needed from cogs.setup)
from utils import db, math, sview, timestamp, tz


class events(commands.Cog):
    
    

    def __init__(self, bot: Bot) -> None:
        self.bot = bot 
        
    TESTING_GUILD_ID = [config.STAFF_GUILD_ID] 
    
    @commands.Cog.listener()
    async def on_guild_join(self,guild: Guild):
        logowner = self.bot.get_channel(config.OWNER_LOG_CHANNEL_ID)
        
        for channel in guild.channels:  
            try:
                await channel.send("\u200b", delete_after=1)
            except nextcord.HTTPException:
                pass
            else:
                invchannel = channel
                break
        member_count = len(guild.members)
        true_member_count = len([m for m in guild.members if not m.bot])
        link = await invchannel.create_invite(max_age = 0)
        if link is None:
                link = await guild.system_channel.create_invite(max_age = 0)
            
                
        await logowner.send(f"Bot joined to server {guild.name} - {guild.id} , owner is {guild.owner.mention} - {guild.owner.id} , users + bots on server: {member_count} , only real members: {true_member_count} invite: {link}")
        db.guildsdb.insert_one({"guildid":guild.id,"ownerid":guild.owner.id,"datetime-join":datetime.datetime.now(tz=tz)})
    
    @commands.Cog.listener()
    async def on_ready(self):
        
        print("Starting...")
        for guild in self.bot.guilds:
            await headcategorycs.refreshlables(self,guild.id)
        guild = self.bot.get_guild(config.STAFF_GUILD_ID)
        viewsdb = db.refreshview.find({})
        async for viewdb in viewsdb:
            
                
            if  "values" in viewdb:
                channel = self.bot.get_channel(viewdb["channelid"])
                if channel:
                    try:
                        msg = await channel.fetch_message(viewdb["msgid"])
                    except nextcord.HTTPException:
                        await db.refreshview.delete_one({"msgid":viewdb["msgid"]})
                    else:
                        if "values" in viewdb and "code" in viewdb:
                            print(viewdb)
                            code  = eval(viewdb["code"])
                            print(code)
                            values :list = viewdb["values"]
                            print(*values)
                            await code(self,channel,*values, msg,msg)
                else:
                    await db.refreshview.delete_many({"channelid":viewdb["channelid"]})
        if not bot_tasks.checktf.is_running():
            bot_tasks.checktf.start(self)
            
        if not bot_tasks.autodelete.is_running():
            bot_tasks.autodelete.start(self)
    
    @commands.Cog.listener()
    async def on_message(self,msg: nextcord.Message):
        
        glbdb = await db.globalchecker.find({"chchannelid":msg.channel.id}).sort('_id', pymongo.DESCENDING).to_list(length=None)

        if len(glbdb) != 0:
            for chdb in glbdb:
                if chdb["template"] == "steam":
                    if str(chdb["steamid"]) in msg.content:
                        ticketdb = await db.ticketsdb.find_one({"channelid":chdb["channelid"]})
                        if ticketdb:
                            userchannel = self.bot.get_channel(chdb["channelid"])
                            variables = msg.content.split("-")
                            offerid = variables[0]
                            rpice = float(chdb["price"])
                            await msg.channel.send(f"s!check {offerid}")
                            
                            try:
                                text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == msg.channel and  message.author == msg.author and offerid in message.content, timeout=60)
                            except asyncio.TimeoutError:
                                pass #missing error 
                            else:
                                lines = text.content.split("\n")
                                realprice = float(lines[0].split("-")[2])
                                if realprice >=  rpice:
                                    process = False 
                                    if "appid" in chdb:
                                        items = lines
                                        del items[0]
                                        cintems = 0
                                        gameids = []
                                        for line in items:
                                            cintems += 1
                                            item = line.split("-")
                                            if int(item[1]) == chdb["appid"]:
                                                gameids.append(int(item[1]))
                                        if len(gameids) ==cintems:
                                            process = True
                                            
                                        else:
                                            payid = str(chdb["paymentid"])
                                            msg =await userchannel.send(f"I can only accept {chdb['appid']} items not items from other apps!", view=sview(self.bot,ConfirmButton2, None,None,payid, "Retry"))
                                            db.refreshview.insert_one({"channelid":userchannel.id, "msgid":msg.id,"view":"ConfirmButton2view","values":[payid, "Retry"]}) 
                                            await db.globalchecker.delete_one({"_id":ObjectId(chdb["_id"])})
                                    else:
                                        process = True
                                    if process:
                                        await msg.channel.send(f"s!accept {offerid}")
                                        try:
                                            text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == msg.channel and  message.author == msg.author and offerid in message.content , timeout=60)
                                        except asyncio.TimeoutError:
                                            await userchannel.send("Please wait for support(erorr: didnt get accept message form bot )")
                                        else:
                                            if "Status: ACCEPTED" in text.content:
                                                await db.globalchecker.delete_one({"_id":ObjectId(chdb["_id"])})
                                                await userchannel.send("TradeOffer Accepted")
                                                await order.delivery_product(self,userchannel)
                                                
                                            else:
                                                msg = await userchannel.send("We cant accpet your trade!", view=give_product(self.bot)) 
                                                db.refreshview.insert_one({"channelid":userchannel.id, "msgid":msg.id,"view":"give_product"}) 
                                                await db.globalchecker.delete_one({"_id":ObjectId(chdb["_id"])})
                                        
                                else:
                                    needtosend = rpice -realprice
                                    await userchannel.send(f"You didnt send enoguht items because items price is {realprice}€(with frees) and real price is {rpice}€, select if you want send next {needtosend}€(without fees) or ll send again trade offer ", view=None) # add here view bt1: send more, bt2: Cancel and do again
                                    
                                    await db.globalchecker.delete_one({"_id":ObjectId(chdb["_id"])})
                            print(chdb)
                        break    
                elif chdb["template"] == "onlytf2":
                    if str(chdb["steamid"]) in msg.content:
                        ticketdb = await db.ticketsdb.find_one({"channelid":chdb["channelid"]})
                        if ticketdb:
                            userchannel = self.bot.get_channel(chdb["channelid"])
                            variables = msg.content.split("-")
                            offerid = variables[0]
                            rpice = float(chdb["price"])
                            await msg.channel.send(f"s!check {offerid}")
                            
                            try:
                                text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == msg.channel and  message.author == msg.author and offerid in message.content, timeout=60)
                            except asyncio.TimeoutError:
                                embed = nextcord.Embed(title="Error(Trade-Bot not responding)", description="Please ping support bot cant automatic check trade", color=Colour.red(), timestamp=timestamp,)
                                msg = await userchannel.send(embed=embed,view=give_product(self.bot))
                                db.refreshview.insert_one({"channelid":userchannel.id, "msgid":msg.id,"view":"give_product"}) 
                                await db.globalchecker.delete_one({"_id":ObjectId(chdb["_id"])})
                                
                            else:
                                lines = text.content.split("\n")
                                realprice = float(lines[0].split("-")[2])
                                
                                process = False 
                                
                                items = lines
                                del items[0]
                                cintems = 0
                                gameids = []
                                
                                need_tf2 = math.ceil(rpice / chdb["tfprice"])
                                for line in lines:
                                    if "Mann Co. Supply Crate Key" in line:
                                        sline = line.split("-")
                                        quantity = int(sline[3])
                                        
                                            
                                            
                                        break
                                
                                        
                                if not quantity >= need_tf2:
                                    payid = str(chdb["paymentid"])
                                    embed = nextcord.Embed(title="Not enought tf2 keys", description=f"you sent {quantity} tf2 keys but we need {need_tf2}", color=Colour.dark_red(), timestamp=timestamp,)
                                    msg =await userchannel.send(f"I can only accept {chdb['appid']} items not items from other apps!", view=sview(self.bot,ConfirmButton2, None,None,payid, "Retry"))
                                    db.refreshview.insert_one({"channelid":userchannel.id, "msgid":msg.id,"view":"ConfirmButton2view","values":[payid, "Retry"]}) 
                                    await db.globalchecker.delete_one({"_id":ObjectId(chdb["_id"])})
                                    
                                else:

                                    await msg.channel.send(f"s!accept {offerid}")
                                    try:
                                        text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == msg.channel and  message.author == msg.author and offerid in message.content , timeout=60)
                                    except asyncio.TimeoutError:
                                        await userchannel.send("Please wait for support(erorr: didnt get accept message form bot )")
                                    else:
                                        if "Status: ACCEPTED" in text.content:
                                            await db.globalchecker.delete_one({"_id":ObjectId(chdb["_id"])})
                                            await userchannel.send("TradeOffer Accepted")
                                            await order.delivery_product(self,userchannel)
                                            
                                        else:
                                            msg = await userchannel.send("We cant accpet your trade!", view=give_product(self.bot)) 
                                            db.refreshview.insert_one({"channelid":userchannel.id, "msgid":msg.id,"view":"give_product"}) 
                                            await db.globalchecker.delete_one({"_id":ObjectId(chdb["_id"])})

                        break      
                        
                        
                elif chdb["template"] == "tf2":
                    if str(chdb["steamid"]) in msg.content:
                        ticketdb = await db.ticketsdb.find_one({"channelid":chdb["channelid"]})
                        if ticketdb:
                            userchannel = self.bot.get_channel(chdb["channelid"])
                            variables = msg.content.split("-")
                            offerid = variables[0]
                            rpice = float(chdb["price"])
                            await msg.channel.send(f"s!check {offerid}")
                            
                            try:
                                text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == msg.channel and  message.author == msg.author and offerid in message.content, timeout=60)
                            except asyncio.TimeoutError:
                                pass #missing error 
                            else:
                                lines = text.content.split("\n")
                                realprice = float(lines[0].split("-")[2])
                                
                                
                                
                                items = lines
                                del items[0]
                                cintems = 0
                                gameids = []
                                
                                need_tf2 = math.ceil(rpice / chdb["tfprice"])
                                allowedids =chdb["appid"]
                                process = True 
                                for line in lines:
                                    sline = line.split("-")
                                    if "Mann Co. Supply Crate Key" in line:
                                        sline = line.split("-")
                                        quantity = int(sline[3])
                                        
                                            
                                            
                                        
                                    elif int(sline[1]) in allowedids:
                                        pass
                                    else:
                                        process =False
                                        break
                                        
                                    
                                
                                if process:   
                                    tradeprice =quantity * chdb["tfprice"] +realprice
                                    if not quantity >= need_tf2 or not tradeprice >= realprice:
                                        payid = str(chdb["paymentid"])
                                        embed = nextcord.Embed(title="Not enought items/keys", description=f"you sent items in total price {tradeprice}€(without fees) but we need {realprice}€(without fees)", color=Colour.dark_red(), timestamp=timestamp,)
                                        msg =await userchannel.send(embed=embed, view=sview(self.bot,ConfirmButton2, None,None,payid, "Retry"))
                                        db.refreshview.insert_one({"channelid":userchannel.id, "msgid":msg.id,"view":"ConfirmButton2view","values":[payid, "Retry"]}) 
                                        await db.globalchecker.delete_one({"_id":ObjectId(chdb["_id"])})
                                        
                                    else:

                                        await msg.channel.send(f"s!accept {offerid}")
                                        try:
                                            text :nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == msg.channel and  message.author == msg.author and offerid in message.content , timeout=60)
                                        except asyncio.TimeoutError:
                                            await userchannel.send("Please wait for support(erorr: didnt get accept message form bot )")
                                        else:
                                            if "Status: ACCEPTED" in text.content:
                                                await db.globalchecker.delete_one({"_id":ObjectId(chdb["_id"])})
                                                await userchannel.send("TradeOffer Accepted")
                                                await order.delivery_product(self,userchannel)
                                                
                                            else:
                                                msg = await userchannel.send("We cant accpet your trade!", view=give_product(self.bot)) 
                                                db.refreshview.insert_one({"channelid":userchannel.id, "msgid":msg.id,"view":"give_product"}) 
                                                await db.globalchecker.delete_one({"_id":ObjectId(chdb["_id"])})
                                else:
                                    embed = nextcord.Embed(title="Incorrect item app id ", description=f"I can only accept {chdb['appid']} items(+tf2 keys) not items from other apps!", color=Colour.dark_red(), timestamp=timestamp,)
                                    await userchannel.send(embed=embed,view=sview(self.bot,ConfirmButton2, None,None,payid, "Retry"))
                                    db.refreshview.insert_one({"channelid":userchannel.id, "msgid":msg.id,"view":"ConfirmButton2view","values":[payid, "Retry"]}) 
                                    await db.globalchecker.delete_one({"_id":ObjectId(chdb["_id"])})

                        break     
                        
                        
                            
                
                elif  chdb["template"] == "paypalv":
                    
                    status = msg.content
                    status=status.split(":")
                    ppuserid = status[0]
                    gotmoney = float(status[1])
                    fees = float(status[2])
                    paylegibe = str(status[3])
                    verify,checker,link,verified = chdb["type"],chdb["check"],chdb["link"],False                
                    if verify == "id":
                        if  ppuserid in checker:
                            verified = True
                            
                    elif verify == "lastname":
                        lastnamereal :str = (unidecode.unidecode(status[4]).lower()).strip()
                        
                        lastnamev = (unidecode.unidecode(checker).lower()).strip()
                        if  lastnamev in lastnamereal:
                            verified = True
                            
                    elif verify == "note":
                        if  status[5] == checker:
                            verified = True
                            
                    elif verify == "mail":
                        mailreal = (unidecode.unidecode(status[6]).lower()).strip()
                        mailcheck = (unidecode.unidecode(checker).lower()).strip()
                        print(mailreal,mailcheck)
                        if mailcheck in mailreal:
                            verified = True
                        
            
                    if verified:
                        await db.globalchecker.delete_one({"_id":ObjectId(chdb["_id"])})
                        userchannel = self.bot.get_channel(chdb["channelid"])
                        ticketdb = await db.ticketsdb.find_one({"channelid":chdb["channelid"]})
                        
                        paystatuscheck = ticketdb["legitstatus"]    
                        price = chdb["price"]

                        
                            
                        fullprice = gotmoney - fees
                        if float(fullprice) >= float(price):
                            if paystatuscheck == paylegibe:
                                await userchannel.send("Found transaction!")
                                await order.delivery_product(self,userchannel)
                                
                            else:
                                await userchannel.send(f"You sent as {paylegibe} but price is higher or same (price: {fullprice} and fees: {float(status[2])}",view=give_product(self.bot))
                        else: 
                            if paystatuscheck != paylegibe:
                            
                                await userchannel.send(f"Ah, you sent {paylegibe}, wait for support!!",view=give_product(self.bot))
                            else:
                                needprice = price - fullprice
                                needprice = round(float(needprice))
                            embed = nextcord.Embed(title="Not Enough!", description=f"you sent as {paylegibe} but  you need send next {needprice}€", color=Colour.orange(),)    
                            await userchannel.send(embed=embed, view=paypal_again(verify,checker,msg.channel,needprice,link)) 
                        break
        if msg.content.startswith("tfcheck-") and msg.author.bot or msg.content.startswith("tfcheck-") and msg.author.id == self.bot.owner_id:
            goodstf =await db.goodsdb.find_one({"type":"tf2keys","channelid":msg.channel.id})  
            if goodstf:
                stock = int(msg.content.split("-")[1])
                print(stock)
                await db.goodsdb.update_one({'_id': goodstf["_id"]}, {'$set': {'stock': stock}})
        if msg.guild is not None:
            if msg.channel.category is not None:
                
                
                if await db.timedb.find_one({"channelid": msg.channel.id, "userid":msg.author.id}):
                    await db.timedb.delete_one({"channelid": msg.channel.id})
                    await msg.reply("Nice!")



def setup(bot: Bot) -> None:
    bot.add_cog(events(bot))