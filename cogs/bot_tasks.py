import datetime
import time

import nextcord
from nextcord import TextChannel
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Bot
from termcolor import cprint

import config
from cogs.helpers import helpers
from utils import db, tz, tzsk


class close_ticket(nextcord.ui.View):
    def __init__(self,bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot 


    # This one is similar to the confirmation button except sets the inner value to `False`
    @nextcord.ui.button(label="Close it!", style=nextcord.ButtonStyle.grey)
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        
        await helpers.close_ticket(self,interaction)
                
                              
                

class bot_tasks(commands.Cog):
    
    

    def __init__(self, bot: Bot) -> None:
        self.bot = bot 
        
    TESTING_GUILD_ID = [config.STAFF_GUILD_ID] 
    
    @tasks.loop(hours=5) 
    async def checktf(self):
        goodstf =await db.goodsdb.find({"type":"tf2keys"}).to_list(length=None)
        for tfgood in goodstf:
            channel = self.bot.get_channel(tfgood["channelid"])
            await channel.send("s!tfcheck")
            
            
    @tasks.loop(hours=1) 
    async def autodelete(self):
        datetime_utc = datetime.datetime.now(tz=tz)
        listof =await db.ticketsdb.find({}).to_list(length=None)
    
        for channeldata in listof:
            channel = self.bot.get_channel(channeldata["channelid"])            
            if channel:
                ivalue = await db.timedb.find_one({"channelid":channel.id})
                wpay =await db.globalchecker.find_one({"channelid":channel.id})
                if  ivalue is None and wpay is None:
                    await bot_tasks.auto_close_process(self,channel,channeldata)
                    
                elif wpay:
                    wdt :datetime.datetime= wpay["datetime"].replace(tzinfo=tz)
                    seconds = abs((datetime_utc-wdt).total_seconds())
                    if seconds >=259200: #if its older than 4days
                        await db.globalchecker.delete_one({"channelid":channel.id})
                        
                        await channel.send(f"<@{self.bot.owner_id}> use donot_close if you dont wanna to delete or cl_ose")
                        await bot_tasks.auto_close_process(self,channel,channeldata)
                                                 
            else:   
                await db.ticketsdb.delete_one({"channelid":channeldata["channelid"]})
                                                             
                                                             
        
        dt = datetime_utc.replace(tzinfo=None)
        timedbs = await db.timedb.find({}).to_list(length=None)
        
            
            
            
        print(f"timedbs = {len(timedbs)}")   
        for tidb in timedbs:
        
            
                datetimes:datetime.datetime = tidb["datetime"]
                
                

                if dt >= datetimes:
                        channel_id = tidb["channelid"]
                        cprint(f"running close for {channel_id}","cyan")
                        channel =  self.bot.get_channel(channel_id)
                        if channel:
                        
                            msgs = (await channel.history(limit=1).flatten())
                            if msgs and len(msgs) != 0:
                                msg = msgs[0]
                                if "close" in msg.content or "donotclose" in msg.content:
                                    await db.timedb.delete_one({"channelid":channel_id})
                                    cprint("donotclose","yellow")
                                    return 
                        if await db.globalchecker.find_one({"channelid":channel_id}) :
                            await db.timedb.delete_one({"channelid":channel_id})
                            cprint("global check","yellow")
                            return 
                        
                        guild = self.bot.get_guild(tidb["guildid"])
                        if guild:
                            if not channel:
                                channel =  guild.get_channel(channel_id)
                            
                            
                            if not channel:
                                cprint("channel non","yellow")
                            
                                await db.timedb.delete_one({"channelid":channel_id})
                            else:
                                print( f" auto close {channel.name} {guild.name}")
                                await helpers.close_ticket(self,None,channel)
                                
                                
                        else:
                            cprint("guild non","yellow")
                            await db.timedb.delete_one({"channelid":channel_id})
                else:
                    print(f"{dt.date()} < {datetimes.date()}")
                    
                    
    async def auto_close_process(self,channel:TextChannel,channeldata:dict):
        cprint(f"Processing deleting for {channel.name}","cyan")
        if msg:= channel.last_message:
                if "close" in msg.content or "donotclose" in msg.content:
                    return 
                
                
            
                
            
                msg_secs = abs(datetime.datetime.now(tz=tz) - msg.created_at).total_seconds() 
                if int(msg_secs) >= 86400:
                    
                    
                    
                        
                        
                    member = channel.guild.get_member(channeldata["userid"])
                    
                    tim2= datetime.datetime.now(tz=tz)+datetime.timedelta(hours=24)
                    timestamp = datetime.datetime.timestamp(tim2)
                    if member is not None:
                        db.timedb.insert_one({"userid":member.id, "channelid":channel.id, "guildid":channel.guild.id,"datetime": tim2})
                        datetimes = datetime.datetime.now(tz=tzsk)+datetime.timedelta(hours=24)
                        
                        await channel.send(f"Hello {member.mention}\n\n> If you want to keep this channel, send here any message or channel will be after <t:{int(time.mktime(datetimes.timetuple()))}:R> automatically deleted!\n\n**Kind Regards,**\n> {channel.guild.name}\n\n**Provided by**\n> {config.BRAND_URL}",view=close_ticket(self.bot))
                    else:
                        tim2= datetime.datetime.now(tz=tz)+datetime.timedelta(hours=1)
                        db.timedb.insert_one({"userid":channeldata["userid"], "channelid":channel.id, "guildid":channel.guild.id,"datetime": tim2})
                        
                    print("ttxxxxxxxt")

                        
                    
                        
        else:
            msgs = (await channel.history(limit=1).flatten())
            if msgs and len(msgs) != 0:
                msg = msgs[0]
                msg_secs = (datetime.datetime.now(tz=tz) - msg.created_at).total_seconds() 
                if int(msg_secs) >= 86400:
                    
                            
                    
                        
                        
                    member = channel.guild.get_member(channeldata["userid"])
                    
                    tim2= datetime.datetime.now(tz=tz)+datetime.timedelta(hours=24)
                    if member :
                        db.timedb.insert_one({"userid":member.id, "channelid":channel.id, "guildid":channel.guild.id,"datetime": tim2})
                        datetimes = datetime.datetime.now(tz=tzsk)+datetime.timedelta(hours=24)
                        
                        await channel.send(f"Hello {member.mention}\n\n> If you want to keep this channel, send here any message or channel will be after <t:{int(time.mktime(datetimes.timetuple()))}:R> automatically deleted!\n\n**Kind Regards,**\n> {channel.guild.name}\n\n**Provided by**\n> {config.BRAND_URL}",view=close_ticket(self.bot))
                    else:
                        tim2= datetime.datetime.now(tz=tz)+datetime.timedelta(hours=1)
                        db.timedb.insert_one({"userid":channeldata["userid"], "channelid":channel.id, "guildid":channel.guild.id,"datetime": tim2})
                        
                    print("ttxxxxxxxt")
                    
            else:
                
                await db.ticketsdb.delete_one({"channelid":channeldata["channelid"]})
                await channel.delete()

def setup(bot: Bot) -> None:
    bot.add_cog(bot_tasks(bot))