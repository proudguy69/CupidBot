# Configuration commands for the bot
from discord import Embed, Member, Message, Interaction, TextChannel, Role
from discord.app_commands import command, describe, Group
from discord.ext.commands import Cog
from database.database import config
import time

class Config(Cog):
    def __init__(self):
        super().__init__()

    config = Group(name="config", description="a group of config commands", default_permissions=None)
    levels = Group(name="levels", description="Subgroup of level config commands", parent=config, default_permissions=None)

    @levels.command(name="channel", description="configure the level up channel")
    @describe(
        channel="the text channel for the level up messages to go"
    )
    async def config_levels_chan(self, interaction: Interaction, channel: TextChannel = None):
        if not channel:
            config.update_one(
                {"server_id": interaction.guild_id},
                {"$unset": {"levelup_chan": ""}},
                upsert=True
            )
            await interaction.response.send_message(f"I have removed the level-up channel setting.")
            return
        else:
            config.update_one(
                {"server_id": interaction.guild_id},
                {"$set": {"levelup_chan": channel.id}},
                upsert=True
            )
            await interaction.response.send_message(f"I have set the level-up channel to {channel.mention}")

    @levels.command(name="reward", description="role rewards for certain level achievements")
    @describe(
        level="The level for this reward",
        roles_added="a list of roles for this reward to acquire, must be separated by a comma",
        roles_removed="a list of roles for this reward to remove, must be separated by a comma"
    )
    async def config_levels_reward(self, interaction: Interaction, level: int, roles_added: str = None, roles_removed: str = None):
        try:
            roles_added_ids = [int(role.strip().strip('<@&').strip('>')) for role in roles_added.split(',')] if roles_added else []
            roles_removed_ids = [int(role.strip().strip('<@&').strip('>')) for role in roles_removed.split(',')] if roles_removed else []
        except ValueError:
            return await interaction.response.send_message("An error occurred! Did you forget to put a ',' between roles?")

        config.update_one(
            {
                "server_id": interaction.guild_id
            },
            {
                "$set": {
                    f"level_rewards.{level}": {
                        "add": roles_added_ids,
                        "remove": roles_removed_ids
                    }
                }
            },
            upsert=True
        )

        roles_added_msg = ", ".join(interaction.guild.get_role(role).mention for role in roles_added_ids) if roles_added_ids else None
        roles_removed_msg = ", ".join(interaction.guild.get_role(role).mention for role in roles_removed_ids) if roles_removed_ids else None

        update_embed = Embed(
            title='Level Rewards',
            description=f"I have updated the roles for level `{level}`!\n\n`+Added:` {roles_added_msg}\n`-Removed:` {roles_removed_msg}"
        )

        await interaction.response.send_message(embed=update_embed)
