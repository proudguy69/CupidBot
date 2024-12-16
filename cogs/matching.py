# Matchmaking features for the bot
from discord import Embed, Member, Message, Interaction
from discord.app_commands import command, Group, guild_only, describe, default_permissions
from discord.ext.commands import Cog
from database import matching as matching_db, generate_profile_description, find_compatible_profiles
from cogs.ui.matchingui import ProfileCreationView, MatchingView

import random


class Matching(Cog):
    def __init__(self) -> None:
        super().__init__()

    
    matching = Group(name="matching", description="group of matching commands")
    profile = Group(name="profile", description="a subgroup of profile based commands", parent=matching)
    pair = Group(name="pair",description="A group of commands to control pairing", parent=matching)

    @pair.command(name="add", description="adds a pair with 2 members")
    @default_permissions(manage_messages=True)
    @describe(
        member_a="The first member to pair",
        member_b="The second member to pair"
    )
    async def pair_add(self, interaction:Interaction, member_a:Member, member_b:Member):
        await interaction.response.defer()
        pair_role = interaction.guild.get_role(1306300320443269190)
        unpair_role = interaction.guild.get_role(1306300431303184434)

        a_roles = set(member_a.roles)
        try:
            a_roles.remove(unpair_role)
            a_roles.add(pair_role)
        except: pass

        b_roles = set(member_b.roles)
        try:
            b_roles.remove(unpair_role)
            b_roles.add(pair_role)
        except: pass

        await member_a.edit(roles=a_roles)
        await member_b.edit(roles=b_roles)

        pairs_channel = interaction.guild.get_channel(1308436302999322704)

    


        await interaction.followup.send(f"I have paired {member_a.mention} + {member_b.mention}! come back in a week to unpair / stay perm pairs")
        matching_db.update_one({'user_id':member_a.id}, {"$set":{"paired":True, "partner_id":member_b.id}})
        matching_db.update_one({'user_id':member_b.id}, {"$set":{"paired":True, "partner_id":member_a.id}})
        await pairs_channel.send(f"✨❤ {member_a.mention} + {member_b.mention} ❤✨")
        




    @command(name="profile", description="Shows the profile of a member")
    @describe(
        member = "The member of the profile you want to see"
    )
    async def profile_command(self, interaction:Interaction, member:Member=None):
        member = member if member else interaction.user
        await interaction.response.defer()

        description, resp_id = generate_profile_description(member.id)

        profile_embed = Embed(title="Profile", description=description, color=0xffa1dc)
        profile_embed.set_author(name=member.name, icon_url=member.avatar.url)
        profile_embed.set_footer(text=f"Profile Id: {resp_id}")
        await interaction.followup.send(embed=profile_embed)
        


    
    @matching.command(name="compatible", description="see all the compatiable profiles")
    async def compatible(self, interaction:Interaction, member:Member=None):
        member = member if member else interaction.user
        if not interaction.guild: return await interaction.response.send_message("you have to use this in a guild!")
        await interaction.response.defer()
        state, data = find_compatible_profiles(member.id, interaction.guild.members)
        if not state:
            return await interaction.followup.send(data)
        profiles = data

        await interaction.followup.send(f"You have `{len(profiles)}` compatible profiles to match with")

    @matching.command(name="unmatch", description="unmatch yourself from your pair")
    async def unmatch(self, interaction:Interaction):
        if not interaction.guild: return await interaction.response.send_message("you have to use this in a guild!")
        await interaction.response.defer(ephemeral=True)

        data:dict = matching_db.find_one({"user_id":interaction.user.id})

        if not data.get('paired'):
            return await interaction.followup.send("You arent even paired! cant unpair", ephemeral=True)
        
        partner_id = data.get('partner_id', 0)

        partner = interaction.guild.get_member(partner_id) # we should check if they are in the server


        matching_db.update_many({
            "user_id": {
                "$in": [interaction.user.id, partner_id]
            }
        },{
            "$unset": {
                "paired":"",
                "partner_id":""
            }
        })

        pair_role = interaction.guild.get_role(1306300320443269190)
        unpair_role = interaction.guild.get_role(1306300431303184434)


        await interaction.user.edit(roles=[role for role in interaction.user.roles if role.id != pair_role.id] + [unpair_role])
        await partner.edit(roles=[role for role in partner.roles if role.id != pair_role.id] + [unpair_role])


        await interaction.followup.send(f"You have successfully unpaired from {partner.mention}")
        

        



    @matching.command(name="match", description="match with people and find a pair!")
    async def match(self, interaction:Interaction):
        if not interaction.guild: return await interaction.response.send_message("you have to use this in a guild!")
        await interaction.response.defer(ephemeral=True)
        
        our_data:dict = matching_db.find_one({'user_id':interaction.user.id})
        if not our_data:
            return await interaction.followup.send("You have no data! use `/matching profile create`")

        if our_data.get('paired'): 
            return await interaction.followup.send("You are already paired, you cant pair again! use `/matching unmatch` to unmatch from your partner!")

        #get our data to compare against
        state, data = find_compatible_profiles(interaction.user.id, interaction.guild.members)
        if not state:
            return await interaction.followup.send(data)
        profiles = data
         

        # get data from the database to pick randomly from
        
        profile:dict = profiles[random.randint(0,len(profiles)-1)]
        user_id = int(profile.get('user_id'))
        member = interaction.guild.get_member(user_id)
        description, resp_id = generate_profile_description(user_id)

        profile_embed = Embed(title="Profile", description=description, color=0xffa1dc)
        profile_embed.set_author(name=member.name, icon_url=member.avatar.url)
        profile_embed.set_footer(text=f"Profile Id: {resp_id}")

        await interaction.followup.send(embed=profile_embed, view=MatchingView(user_id), ephemeral=True)


    


    @profile.command(name="create")
    async def profile_create(self, interaction:Interaction):    
        if not interaction.guild: return await interaction.response.send_message("you have to use this in a guild!")
        await interaction.response.defer(ephemeral=True)

        description, resp_id = generate_profile_description(interaction.user.id)
        profile_embed = Embed(title="Profile", description=description, color=0xffa1dc)
        profile_embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        profile_embed.set_footer(text=f"Profile Id: {resp_id}")

        await interaction.followup.send(embed=profile_embed, view=ProfileCreationView(), ephemeral=True)
    
    @profile.command(name="delete")
    async def profile_delete(self, interaction:Interaction):       

        matching_db.delete_one({"user_id":interaction.user.id})

        await interaction.response.send_message("Your profile has been deleted! Whoops sorry for no confirm deletion button", ephemeral=True)
    

    @profile.command(name="status",description="See the status of your profile")
    async def profile_status(self, interaction:Interaction):       
        if not interaction.guild: return await interaction.response.send_message("you have to use this in a guild!")
        data:dict = matching_db.find_one({'user_id':interaction.user.id})
        if not data: return await interaction.response.send_message("You havent even submitted a profile")
        status = data.get('approved')
        if not status: return await interaction.response.send_message("Your profile isnt submitted, use `/matching profile create` to submit it")
        await interaction.response.send_message(f"Your approval status: `{status}`\n\nFalse means it hasnt been approved yet, if its been more then 3 hours @ping the mods to see if it was submitted properly, if not resubmit it\nTrue means it was submitted :thumbsup:")
        


