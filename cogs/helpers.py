import io
import re

import chat_exporter
import nextcord
from nextcord import Embed, Interaction, TextChannel, User
from nextcord.ext import commands
from nextcord.ext.commands import Bot

import config
from utils import db, is_number, logo


class retry_button(nextcord.ui.View):
    def __init__(self, bot:Bot,view,product,paymentss,schannel):
        super().__init__()
        self.bot = bot
        self.view = view
        self.product = product
        self.paymentss = paymentss
        self.schannel = schannel
        
    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @nextcord.ui.button(label="Retry", style=nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        view = self.view
        
        await interaction.response.send_modal(view)
        
        self.stop()
        
        
        


class ConfirmButton(nextcord.ui.View):
    def __init__(self, bot:Bot,text_question):
        super().__init__(text_question)
        self.bot =bot 
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @nextcord.ui.button(label='Confirm', style=nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction, text_question):
        await interaction.response.send_message('Confirming', ephemeral=True)
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @nextcord.ui.button(label='Change', style=nextcord.ButtonStyle.grey)
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction, text_question):
        await interaction.response.send_message(text_question, ephemeral=False)
        self.value = False
        self.stop()
        await interaction.response.send_modal()
    
     

class Confirm_clear(nextcord.ui.View):
    def __init__(self,bot:Bot):
        super().__init__()
        self.bot = bot
        self.value = None


    @nextcord.ui.button(label="Confirm", style=nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("Confirming", ephemeral=True)
        self.value = True
        self.stop()

    @nextcord.ui.button(label="Cancel", style=nextcord.ButtonStyle.red)
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("Cancelling", ephemeral=True)
        self.value = False
        self.stop()
                
                              
                

class helpers(commands.Cog):
    
    

    def __init__(self, bot: Bot) -> None:
        self.bot = bot 
        
    async def close_ticket(self,interaction:Interaction=None,channel: TextChannel = None,deleter:User = None):
        if interaction:
            channel = interaction.channel
            send = interaction.send
            deleter = interaction.user
        else:
            deleter = self.bot.user
            
            send = channel.send
        test = db.ticketsdb.find_one({"channelid":channel.id})
        if test :
            glcheck = db.globalchecker.find_one({"channelid":channel.id})
            db.globalchecker.delete_one({"channelid":channel.id}) if glcheck else ... 
            if "type" in test and test["type"] == "tf2keys" and "status" not in test  or "type" in test and test["type"] == "tf2keys" and  "status" in  test and  test["status"] != "finished":
                db.goodsdb.update_one({"guilds":channel.guild.id, "type":"tf2keys"},{'$inc': {"onhold":-int(test["amount_thing"])}})
            
            await send("deleteing in 5s")
            transcript = await chat_exporter.export(channel,limit=0)
            

            if transcript is None:
                return
        
            
            transcript_file = nextcord.File(io.BytesIO(transcript.encode()),filename=f"transcript-{channel.name}.html",)
            logchannel = self.bot.get_channel(config.TRANSCRIPT_LOG_CHANNEL_ID)
            embed=nextcord.Embed(title="Deleted channel- command",description="", color=0x00ff2a)
            embed.set_thumbnail(url=logo)
            embed.add_field(name="Channel Name: ", value=channel.name, inline=True)
            embed.add_field(name="Opened By", value=test["userid"], inline=True)
            embed.add_field(name="Server:", value=f"{channel.guild} - `{channel.guild.id}`", inline=True)
            embed.add_field(name="Deleted by", value=deleter.mention, inline=True)
            await logchannel.send(content=test,embed=embed,file=transcript_file)
            await channel.delete(reason=f"{deleter} used /delete")
            
            
            db.ticketsdb.delete_one({"channelid":channel.id})
                    
        else:
            await send("this channel is not in db" )          
    
    
  
    async def waitforrespon(self, channel : nextcord.TextChannel, user : nextcord.Member or nextcord.User = None ,check: str = "msg" ,timeout: float=180):
        
        try:
            if user:
                msg : nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == channel and  message.author.id == user.id  or type(message.channel) == nextcord.channel.DMChannel and message.author.id == user.id, timeout=timeout)
            else:
                msg : nextcord.Message = await self.bot.wait_for('message', check=lambda message: message.channel == channel or type(message.channel) == nextcord.channel.DMChannel and message.author.id == user.id, timeout=timeout)
            
        except Exception:
            
            
            embed=nextcord.Embed(title="error | Your Time ran out", description="Cancelled the Operation!", color=0xff0000)
            embed.set_footer(text=config.BRAND_FOOTER,icon_url=config.BRAND_LOGO_URL)
                
            await channel.send(embed=embed)
            return None
        else:
            if check == "msg":
                return msg 
            elif check == "channel":
                if msg.channel_mentions:
                    channelg = msg.channel_mentions[0]
                    

                    return channelg , msg 

                else:
                    if is_number(msg.content):
                        channelg = self.bot.get_channel(int(msg.content))
                        if channelg:
                            return channelg , msg 
                        else:
                            return None, msg 


                    embed=Embed(title="error | invalid channel!!", description="Cancelled the Operation!", color=0xff0000)
                    embed.set_footer(text=config.BRAND_FOOTER,icon_url=config.BRAND_LOGO_URL)
                    await channel.send(embed=embed)
                    return None, msg 
            elif check == "user":
                if msg.mentions:
                    user = msg.mentions[0]
                    

                    return user , msg 

                else:
                    if is_number(msg.content):
                        userg = self.bot.get_user(int(msg.content))
                        if userg:
                            return userg, msg 
                        else:
                            return None, msg 


                    embed=Embed(title="error | invalid channel!!", description="Cancelled the Operation!", color=0xff0000)
                    embed.set_footer(text=config.BRAND_FOOTER,icon_url=config.BRAND_LOGO_URL)
                    await channel.send(embed=embed)
                    return None, msg 
            elif check == "member":
                if msg.mentions:
                    member = msg.mentions[0]
                    

                    return member ,msg

                else:
                    if is_number(msg.content):
                        member = channel.guild.get_member(int(msg.content))
                        if member:
                            return member, msg
                        else:
                            return None, msg 


                    embed=Embed(title="error | invalid channel!!", description="Cancelled the Operation!", color=0xff0000)
                    embed.set_footer(text=config.BRAND_FOOTER,icon_url=config.BRAND_LOGO_URL)
                    await channel.send(embed=embed)
                    return None, msg 
            elif check == "int":
                if msg.content.isnumeric():
                    number = int(msg.content)
                    return number, msg
                else:
                    embed=Embed(title="error | value isn't numeric(only integers)", description="Cancelled the Operation!", color=0xff0000)
                    embed.set_footer(text=config.BRAND_FOOTER,icon_url=config.BRAND_LOGO_URL)
                    await channel.send(embed=embed)
                    return None, msg
                
            elif check == "float":
                if is_number(msg.content):
                    number = float(msg.content)
                    return number, msg
                
                else:
                    embed=Embed(title="error | value isn't numeric", description="Cancelled the Operation!", color=0xff0000)
                    embed.set_footer(text=config.BRAND_FOOTER,icon_url=config.BRAND_LOGO_URL)
                    await channel.send(embed=embed)
                    return None, msg 
            elif check == "hex":
                color = msg.content
                match = re.search(r'^#(?:[0-9a-fA-F]{1,2}){3}$', color)
                if match:
                    color=int(color.replace("#", ""), 16)
                    return color, msg
                    
                    
                else:
                    embed=Embed(title="error | Incorrect color hex format", description="Cancelled the Operation!", color=0xff0000)
                    embed.set_footer(text=config.BRAND_FOOTER,icon_url=config.BRAND_LOGO_URL)
                    await channel.send(embed=embed)
                    return None, msg
            elif check == "image_n":
                regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
                rx = re.findall(regex,msg.content)
                urls = [x[0] for x in rx]
                if urls and urls[0]:
                    url = str(urls[0])
                    if url.endswith([".png",".jpg","jpeg",".gif",".webm",".mp4",".ogg",".wav",".gifv",".PNG",".JPG" ".JPEG",]):
                        return url , msg
                elif msg.content.startswith("0") or msg.content.startswith("no"):    
                    return 0 , msg 
                
                else:
                    embed=Embed(title="ERROR | incorrect link", description="Cancelled the Operation!", color=0xff0000)
                    embed.set_footer(text=config.BRAND_FOOTER,icon_url=config.BRAND_LOGO_URL)
                    await channel.send(embed=embed)
                    return None, msg 
                    
                    



def setup(bot: Bot) -> None:
    bot.add_cog(helpers(bot))