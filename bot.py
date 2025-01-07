from discord.ext.commands import Bot, is_owner, Context
from discord import Intents, Embed, Message, Member
from settings import TOKEN
import asyncio

#Cog Modules
from cogs.levels import Levels
from cogs.moderation import Moderation
from cogs.config import Config
from cogs.matchingv2 import Matching
from cogs.roles import RoleView
from cogs.welcome import Welcome
from cogs.ui.submissionui import SubmissionView

from database.matchingdb import MATCHING, Profile



class Bot(Bot):
    def __init__(self):
        super().__init__(command_prefix='?', intents=Intents.all())

    async def setup_hook(self) -> None:
        self.add_view(RoleView())
        self.add_view(SubmissionView(self))
        await self.add_cog(Levels(self))
        await self.add_cog(Moderation(self))
        await self.add_cog(Config())
        await self.add_cog(Matching(self))
        await self.add_cog(Welcome())




bot = Bot()
tree = bot.tree



@bot.command()
async def pfp(ctx:Context):
    await ctx.send(f"`{ctx.author.avatar.url}`")

@bot.command()
@is_owner()
async def send_roles(ctx:Context):
    
    description = """
    Select a color from any of the options below

    <:White:1307861241536057385> <@&1307855860034306068>
    <:Pink:1307861237719240868> <@&1307856243314004028>
    <:Red:1307861240684478614> <@&1307855826173694013>
    <:Orange:1307861236431589468> <@&1307855837385064478> 
    <:Yellow:1307861278336749588> <@&1307855838802870362>
    <:Green:1307861235177492501> <@&1307855840262361160> 
    <:Blue:1307861233873195148> <@&1307855841491288086> 
    <:Purple:1307861239413604383> <@&1307855850836070460> 
    <:Black:1307861232887267358> <@&1307855861577809990>
    """.strip()

    role_embed = Embed(title='Color Roles', description=description, color=0xffa1dc)
    await ctx.send(embed=role_embed, view=RoleView())


@bot.command()
@is_owner()
async def purge_profiles(ctx:Context):
    members:list[Member] = bot.get_all_members()
    profiles = MATCHING.find()
    member_ids = [member.id for member in members]
    profile_ids = [profile.get('user_id', 0) for profile in profiles if profile.get('user_id', 0) not in member_ids]
    result = MATCHING.delete_many({"user_id": {"$in":profile_ids}})

    await ctx.send(f"Deleted {result.deleted_count} profiles!")
    

from collections import Counter


@bot.command()
@is_owner()
async def duplicate_check(ctx:Context, user_id:int):
    profile:dict = MATCHING.find_one({"user_id":954513064571584554})
    rejected = profile.get('rejected_pairs', [])

    counts = Counter(rejected)


    duplicates = {item: count for item, count in counts.items() if count > 1}
    total_duplicates = sum(count - 1 for count in duplicates.values())
    await ctx.send(total_duplicates)




@bot.command()
@is_owner()
async def sync(ctx:Context):
    msg = await ctx.send("Syncing..")
    await tree.sync()
    await msg.edit(content="Done!")


bot.run(TOKEN)