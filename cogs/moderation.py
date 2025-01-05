#Moderation Features for the bot
from discord import Embed, Member, Message, Interaction, Attachment, User
from discord.app_commands import command, describe, Group, default_permissions
from discord.ext.commands import Cog, Bot

from database.moderationdb import create_case, get_cases, Case

import time
import datetime
import re
from enum import Enum


class CaseType(Enum):
    warn = "warn"
    timeout = "timeout"
    kick = "kick"
    soft_ban = "soft_ban"
    ban = "ban"

    


class Moderation(Cog):
    def __init__(self, bot:Bot) -> None:
        super().__init__()
        self.bot = bot



    case = Group(name='case',description="A group of all case related commands")

    async def process_warn(self, user:User, reason:str):
        try: await user.send(f"You've been warned for: `{reason}`")
        except: pass

    async def process_duration(self, duration:str) -> int:
        if duration == None: return 86400
        dur_str = duration.replace(',','').replace(' ','')

        time_periods = {
            "s": 1,
            "m": 60,
            "h": 3600,
            "d": 86400,
            "w": 604800
        }

        pattern = r"(\d+)([smhdw])"
        matches = re.findall(pattern, dur_str)

        total_seconds = 0
        for amount, unit in matches:
            total_seconds += int(amount) * time_periods[unit]

        return total_seconds
    
    async def process_timeout(self, user:User, reason:str, duration:str):
        try: await user.send(f"you were timed out for `{reason}`")
        except:pass
        

    @case.command(name="create", description="creates a case against a user")
    @default_permissions(manage_messages=True)
    @describe(
        user="The user to create a case on",
        type="The type of case to create",
        reason="The reason for this case's creation",
        duration="The duration in 1d 5h 3s format",
        proof="Attached proof for this infraction"
    )
    async def case_create(self, interaction:Interaction, user:Member, type:CaseType, reason:str="None Provided", duration:str=None, proof:Attachment=None):
        await interaction.response.defer()
        if 1306410068253868032 not in [role.id for role in interaction.user.roles]: return await interaction.followup.send("Only staff can run this command!")
        
        match type.value:
            case CaseType.warn.value:
                await self.process_warn(user, reason)
            case CaseType.timeout.value:
                timeout_time = await self.process_duration(duration)
                await user.timeout(datetime.timedelta(seconds=timeout_time))
                self.process_timeout(user, reason)
            case CaseType.kick.value:
                pass
                
        case:Case = create_case(self.bot, interaction.guild_id, type.value, user, interaction.user, reason)
        await case.log_action()
        await interaction.followup.send(embed=case.embed)
    @case_create.error
    async def case_create_error(self, interaction:Interaction, error):
        await interaction.followup.send(f"An error has occured:\n\n```{error}```")

    

    @case.command(name='view', description="View all the cases a user has")
    @default_permissions(manage_messages=True)
    async def case_view(self, interaction:Interaction, user:User):
        if 1306410068253868032 not in [role.id for role in interaction.user.roles]: return await interaction.response.send_message("Only staff can run this command!")
        cases = get_cases(self.bot, user)
        data = {
            True: "...",
            False: ""
        }
        description = "\n".join(f"`{case.id}` | `{case.type}` | `{case.reason[0:20]}{data[len(case.reason) > 20]}`" for case in cases) if len(cases) > 0 else "No cases found!"
        cases_embed = Embed(title=f"All cases for {user.name}", description=description, color=0xffd5a6)
        await interaction.response.send_message(embed=cases_embed)


        
