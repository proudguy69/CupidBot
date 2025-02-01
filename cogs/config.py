#Configuration commands for the bot
from discord import Embed, Member, Message, Interaction, TextChannel, Role
from discord.app_commands import command, describe, Group, default_permissions
from discord.ext.commands import Cog, Bot
from database.configdb import get_config

from enum import Enum


class ChannelType(Enum):
    moderation_logs = "Moderation Logs"
    action_logs = "Action Logs"
    

class RoleType(Enum):
    suspended = "Suspended"
    staff = "Staff"


class Config(Cog):
    def __init__(self, bot:Bot):
        self.bot = bot
        super().__init__()
    
    config = Group(name="config", description="a group of config commands", default_permissions=None)
    levels = Group(name="levels", description="Subgroup of level config commands", parent=config, default_permissions=None)
    moderation = Group(name="moderation", description="Subgroup of moderation config commands", parent=config, default_permissions=None)


    # level configuration
    @levels.command(name="channel", description="configure the level up channel")
    @default_permissions(administrator=True)
    @describe(
        channel="the text channel for the leveup messages to go"
    )
    async def config_levels_chan(self, interaction:Interaction, channel:TextChannel=None):
        config_obj = get_config(self.bot, interaction.guild_id)
        if not channel:
            config_obj.edit({"$unset": {"levelup_chan":""}}, upsert=True)
            await interaction.response.send_message(f"I have set the levelup channel to {channel}")
            return
        else:
            config_obj.edit({"$set":{"levelup_chan":channel.id}}, upsert=True)
            await interaction.response.send_message(f"I have set the levelup channel to {channel.mention}")
    


    @levels.command(name="reward", description="role rewards for certain level achivements")
    @default_permissions(administrator=True)
    @describe(
        level="The level for this reward",
        roles_added="a list of roles for this reward to acquire, must be seperated by a comma",
        roles_removed="a list of roles for this reward to remove, must be seperated by a comma"
    )
    async def config_levels_reward(self, interaction:Interaction, level:int, roles_added:str=None, roles_removed:str=None):
        config = get_config(self.bot, interaction.guild_id)
        try:
            roles_added_ids = [int(role.strip().strip('<@&').strip('>')) for role in roles_added.split(',')] if roles_added else []
            roles_removed_ids = [int(role.strip().strip('<@&').strip('>')) for role in roles_removed.split(',')] if roles_removed else []
        except:
            return await interaction.response.send_message("An error occured! did you forget to put a , between roles?")
        
       
        config.edit(
        {
            "$set": {
                f"level_rewards.{level}": 
                {
                    "add":roles_added_ids,
                    "remove":roles_removed_ids
                } 
            }
        }, upsert=True)

        
        roles_added_msg = ", ".join(interaction.guild.get_role(role).mention for role in roles_added_ids) if roles_added_ids else None
        roles_removed_msg = ", ".join(interaction.guild.get_role(role).mention for role in roles_removed_ids) if roles_removed_ids else None

        update_embed = Embed(title='Level Rewards', description=f"I have updated the roles for level `{level}`!\n\n`+Added:` {roles_added_msg}\n`-Removed:` {roles_removed_msg}")
        
        await interaction.response.send_message(embed=update_embed)

    @moderation.command(name="set_channel", description="sets default channels for certain logging actions")
    @default_permissions(administrator=True)
    @describe(type="the logging type to set the logging of", channel="the channel to subscribe the type too")
    async def moderation_set_channel(self, interaction:Interaction, type:ChannelType, channel:TextChannel=None):
        config = get_config(self.bot, interaction.guild_id)

        #control variables
        _set = "$set" if channel else "$unset"
        channel_id = channel.id if channel else  ''
        mention = channel.mention if channel else '`None`'

        match type.value:
            case ChannelType.moderation_logs.value:
                config.edit({_set:{"mod_logs_channel":channel_id}})
            case ChannelType.action_logs.value:
                config.edit({_set:{"action_logs_channel":channel_id}})
        

        
        config_update = Embed(title="Config Update", description=f"Updated `{type.value} Channel` to: {mention}")


        await interaction.response.send_message(embed=config_update)
    


    @moderation.command(name="set_role", description="sets default roles and staff roles for certain moderation actions")
    @default_permissions(administrator=True)
    @describe(type="the type of role to set of", role="the role to set the type of")
    async def moderation_set_channel(self, interaction:Interaction, type:RoleType, role:Role):
        config = get_config(self.bot, interaction.guild_id)



        


        await interaction.response.send_message(f"I have set `{type.value}` to `{role.name}`")
