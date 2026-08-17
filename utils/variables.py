

# (nothing needed from utils.mongodb)
import datetime
import math
from decimal import Decimal
from itertools import cycle

import nextcord
from nextcord import Member, SelectOption, User
from nextcord.ext.commands import Bot

import config


class mview(nextcord.ui.View):
        def __init__(self,bot:Bot,item: nextcord.ui.Select,item2: nextcord.ui.Select,user:nextcord.User or nextcord.Member,timeout = None, *args):
            super().__init__(timeout=timeout)
            self._user = user
            self.bot = bot 
            
             
            
        
            print(len(args))
            args1 = []
            args2 = []
            listargs = cycle([1,2])
            for arg in args:
                number = next(listargs)
                if int(number) == 1:
                    args1.append(arg)
                else:
                    args2.append(arg)
                    
                
                
            self.add_item(item(bot, *args1))
            self.add_item(item2(bot, *args2))
        async def on_timeout(self):
            print("mview ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc")
            self.clear_items()
        async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
            if self._user is not None:
                variable = interaction.user == self._user
                if not variable:
                    embed=nextcord.Embed(title="error", description=f"**This `Selection` only can use {self._user.mention}**", color=nextcord.Colour.orange())
                    await interaction.send(embed=embed, ephemeral=True)
        
                return variable
            return True

class sview(nextcord.ui.View):
        def __init__(self,bot:Bot,item: nextcord.ui.Select,user:nextcord.User or nextcord.Member,timeout:float or None = None, *args):
            super().__init__(timeout=timeout)
            self._user = user
            self.bot = bot 
            
             
            
        
            print(len(args))
            self.add_item(item(self.bot, *args))
        async def on_timeout(self):
            self.clear_items()
            
        async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
            if self._user is not None:
                variable = interaction.user == self._user
                if not variable:
                    embed=nextcord.Embed(title="error", description=f"**This `Selection` only can use {self._user.mention}**", color=nextcord.Colour.orange())
                    await interaction.send(embed=embed, ephemeral=True)
        
                return variable
            return True

class wview(nextcord.ui.View):
        def __init__(self,item: nextcord.ui.Select,user:nextcord.User or nextcord.Member, timeout:float or None = 120,*args):
            super().__init__(timeout=timeout)
            self._user = user
            
            
             
            
        
            
            self.add_item(item( *args))
        async def on_timeout(self):
            print("wview ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc")
            self.clear_items()
        async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
            if self._user is not None:
                variable = interaction.user == self._user
                if not variable:
                    embed=nextcord.Embed(title="error", description=f"**This `Selection` only can use {self._user.mention}**", color=nextcord.Colour.orange())
                    await interaction.send(embed=embed, ephemeral=True)
        
                return variable
            return True
        


def remove_exponent(d):
    """Remove exponent."""
    return d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()


def millify(n, precision=0, drop_nulls=True, prefixes=[]):
    """Humanize number."""
    millnames = ['', 'k', 'M', 'B', 'T', 'P', 'E', 'Z', 'Y']
    if prefixes:
        millnames = ['']
        millnames.extend(prefixes)
    n = float(n)
    millidx = max(0, min(len(millnames) - 1,
                         int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))
    result = '{:.{precision}f}'.format(n / 10**(3 * millidx), precision=precision)
    if drop_nulls:
        result = remove_exponent(Decimal(result))
    return '{0}{dx}'.format(result, dx=millnames[millidx])
        
        
async def can_dm_user(user: nextcord.User) -> bool:
    ch = user.dm_channel
    if ch is None:
        ch = await user.create_dm()

    try:
        await ch.send()
    except nextcord.Forbidden:
        return False
    except nextcord.HTTPException:
        return True     



timestamp = datetime.datetime.now()
bluepr = config.BRAND_COLOR
tz = datetime.timezone(datetime.timedelta(hours=0))
tzsk = datetime.timezone(datetime.timedelta(hours=2))
logo = config.BRAND_LOGO_URL
server_name = config.BRAND_NAME

# CS:GO competitive ranks. granks: name -> index, nranks: index -> name,
# eranks: index -> emoji. All three share the same indexing, 0 = unranked.
granks = {"u":0,"s1":1,"s2":2,"s3":3,"s4":4,"se":5,"sem":6,"gn1":7,"gn2":8,"gn3":9,"gn4":10,"mg1":11,"mg2":12,"mge":13,"dmg":14,"le":15,"lem":16,"smfc":17,"ge":18}
nranks = {index: name for name, index in granks.items()}
# The original eranks was shifted by one against nranks: index 0 held the
# Silver 1 emoji and index 1 held the literal text "s1", so an unranked
# customer displayed as Silver 1 and a Silver 1 customer displayed as raw text.
eranks = config.RANK_EMOJIS
TESTING_GUILD_ID = config.TESTING_GUILD_IDS

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        
        return False

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        
        return False
 
def get_user_avatar(user: Member or User ):
    if    user.avatar:
            return user.avatar.url
    else:
            return user.default_avatar.url   
    
def round_up(n, decimals=2):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

def word_count(str:str):
    counts = dict()
    words = str.split()

    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1

    return counts



def rank_options(indices=None):
    """Build a fresh SelectOption list for the CS:GO competitive ranks.

    The original repeated this 18-item list four times in cogs/order.py. New
    objects are built on every call on purpose - nextcord mutates SelectOption
    (it sets `default`), so sharing one list between views leaks state.
    """
    if indices is None:
        indices = range(1, 19)
    return [
        SelectOption(label=config.RANK_LABELS[i], emoji=config.RANK_EMOJIS[i], value=i)
        for i in indices
    ]

embeds = { "1-Setup":{"content":"setup"},
}
