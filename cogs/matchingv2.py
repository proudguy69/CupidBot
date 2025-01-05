from database.matchingdb import NoProfileException, UserNotFoundException, get_profile, MATCHING, NoCompatibleProfilesError
from discord.app_commands import Group, describe, default_permissions, guild_only
from discord import Embed, Member, Interaction, TextChannel, NotFound
from discord.ext.commands import Cog, command, Bot
from discord.ext import tasks
from cogs.ui.profileui import TosConfirmationView, ProfileCreationView
from cogs.ui.matchingui import SwipeView

import random




tos_description = """
1.) Cupid Bot is designed to help users connect and make new friends in a fun and safe environment.

2.) The bot is strictly for friendship-based matchmaking and is not intended for romantic or dating purposes.

3.) Attempting to use Cupid Bot for dating or any activity that violates Discord's Terms of Service, including inappropriate conduct, may result in action being taken by discord, including potential bans. By using Cupid Bot, you agree to respect these guidelines and the community standards.

4.) Cupid bot will not enforce these guidelines and wont go after anyone, by agreeing you understand and agree to the risk involved.
"""

TOS = Embed(title="Terms Of Service", description=tos_description, color=0xff0000)


class Matching(Cog):
    def __init__(self, bot:Bot):
        super().__init__()
        self.bot:Bot = bot


    


    matching = Group(name="matching", description="A group of commands for match making")
    profile = Group(name="profile", description="a subgroup of profile based commands", parent=matching)

    @profile.command(name='create', description='a command to create a profile')
    @guild_only()
    async def profile_create(self, interaction:Interaction):
        try:
            profile = get_profile(interaction.user, self.bot)
        except NoProfileException:
            return await interaction.response.send_message(embed=TOS, view=TosConfirmationView(interaction.user, self.bot), ephemeral=True)
        if not profile.tos:
            return await interaction.response.send_message(embed=TOS, view=TosConfirmationView(interaction.user, self.bot), ephemeral=True)
            
        if profile.approved == False or profile.approved:
            return await interaction.response.send_message("Your profile is already submitted and/or created~! use `/matching profile edit` to edit it!", ephemeral=True)
        
        await interaction.response.send_message(embed=profile.generate_embed(), view=ProfileCreationView(self.bot), ephemeral=True)
    

    @profile.command(name='edit', description='a command to edit a profile')
    @guild_only()
    async def profile_edit(self, interaction:Interaction):
        try:
            profile = get_profile(interaction.user, self.bot)
        except NoProfileException:
            return await interaction.response.send_message("You haven't created a profile! use `/matching profile create`")
        
        await interaction.response.send_message(embed=profile.generate_embed(), view=ProfileCreationView(self.bot, True), ephemeral=True)



    @profile.command(name='load', description="loads your profile from a message")
    @guild_only()
    @describe(channel="The channel where the message is stored",message_id = 'the message id of the embed that has your profile')
    async def profile_load(self, interaction:Interaction, channel:TextChannel, message_id:str):
        try:
            message = await channel.fetch_message(int(message_id))
        except NotFound:
            return await interaction.response.send_message("You provided a WRONG message_id, please watch the video in annoucements")

        factored_desc = message.embeds[0].description.replace("❥﹒", '').replace(':', '').replace("Name", '').replace("Pronouns", '').replace("Name", '').replace("Gender", '').replace("Age", '').replace("Sexuality", '').replace("Bio", '').replace('User', '').replace('|', '\n').replace('`','').split('\n')
        data = "\n".join(sub.strip() for sub in factored_desc)
        fragmented_data = data.split('\n')
        if len(fragmented_data) <6:
            return await interaction.response.send_message("You provided a WRONG message_id, please rewatch the video in annoucements")
        bio = "\n".join(fragmented_data[6::])
        
        
        MATCHING.update_one({"user_id": interaction.user.id}, {
            "$set": {
                "name": fragmented_data[1],
                "pronouns": fragmented_data[2],
                "gender": fragmented_data[3],
                "age": fragmented_data[4],
                "sexuality": fragmented_data[5],
                "bio":bio,
                "tos_agreed":True}
        }, upsert=True)

        await interaction.response.send_message("Done! Your profile is loaded into the database, check back in a few days then run `/matching profile edit` to resubmit it, we are gonna wait a few days until the new system is tested and ready")
        



    @profile.command(name="view", description="view the profile of yourself or another user")
    @guild_only()
    @describe(
        member = "The member of the profile you want to see"
    )
    async def matching_profile_view(self, interaction:Interaction, member:Member=None):
        member = member if member else interaction.user
        await interaction.response.defer()
        try:
            profile = get_profile(member, self.bot)
        except UserNotFoundException: return await interaction.followup.send("The user for the profile was not found! the user is out of scope of the bot")
        except NoProfileException: return await interaction.followup.send(f"{member.mention} does not have a profile!")
        await interaction.followup.send(embed=profile.generate_embed())



    @profile.command(name="delete", description="Deletes your profile")
    async def profile_delete(self, interaction:Interaction):
        return await interaction.response.send_message('command still under construction! check back later', ephemeral=True)
    


    @profile.command(name="status",description="See your approval status for your profile")
    @guild_only()
    @describe(
        member = "The member of the profile's status you want to see"
    )
    async def profile_status(self, interaction:Interaction, member:Member=None):
        if interaction.user.id != 1267552151454875751: return await interaction.response.send_message('command still under construction! check back later', ephemeral=True)
        member = member if member else interaction.user
        profile_data = get_profile(member)
        if not profile_data: return await interaction.response.send_message("You have no profile, try `/matching profile create`")
        status = profile_data.get('approved')

        match status:
            case True:
                await interaction.response.send_message("Your profile is already approved! feel free to use `/matching match`",ephemeral=True)
            case False:
                await interaction.response.send_message("Your profile is not approved! please edit and resubmit your profile via `/matching profile edit`", ephemeral=True)
            case 'waiting':
                await interaction.response.send_message("Staff hasnt gotten to approving your profile yet! please be paitent!", ephemeral=True)
            case _:
                await interaction.response.send_message("Your profile hasnt been submitted! use `/matching profile create` to submit it!`", ephemeral=True)



    @matching.command(name="compatible", description="see all the compatiable profiles")
    @guild_only()
    async def compatible(self, interaction:Interaction, member:Member=None):
        if interaction.user.id != 1267552151454875751: return await interaction.response.send_message('command still under construction! check back later', ephemeral=True)
        member = member if member else interaction.user
        profile = get_profile(member, self.bot)
        compatible = profile.get_compatible_profiles()
        total = len(compatible)
        await interaction.response.send_message(f"You currently have `{total}` compatible profiles! (this excludes profiles you swiped right on)")
    
        
        
    


    @matching.command(name="compatible_view", description="see all the compatiable profiles")
    @default_permissions()
    async def compatible_view(self, interaction:Interaction, member:Member=None):
        if interaction.user.id != 1267552151454875751: return await interaction.response.send_message('this command is reserved for the owner only. it will be hidden soon~ish', ephemeral=True)

        
        



    @matching.command(name="match", description="match with people and find a pair!")
    @guild_only()
    async def match(self, interaction:Interaction):
        try: profile = get_profile(interaction.user, self.bot)
        except NoProfileException: return await interaction.response.send_message(f"You have no profile! use `/matching profile create` to make one", ephemeral=True)
        if profile.approved != True: return await interaction.response.send_message("Your profile hasnt been approved yet", ephemeral=True)

        try: random_profile = profile.get_random_profile()
        except NoCompatibleProfilesError: return await interaction.response.send_message("You are out of profiles to match with! :3", ephemeral=True)
        await interaction.response.send_message(embed=random_profile.generate_embed(), view=SwipeView(random_profile.user, self.bot), ephemeral=True)
        

        
    
    @matching.command(name="purge", description="purge all the people you swiped right or left on")
    @guild_only()
    async def matching_purge(self, interaction:Interaction):
        if interaction.user.id != 1267552151454875751: return await interaction.response.send_message('command still under construction! check back later', ephemeral=True)
        await interaction.response.defer()
        profile = get_profile(interaction.user, self.bot)
        

        result = MATCHING.update_many(
            {'user_id': {'$in': profile.selected_pairs}},
            {'$pull': {'paired_with_us': interaction.user.id}}
        )

        profile.edit({"$set": {"selected_pairs": [], "rejected_pairs": []}})
        
        await interaction.followup.send(f"I have removed `{result.matched_count}`!")
