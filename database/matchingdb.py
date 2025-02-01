from discord import Embed, Member, Message, User
from discord.ext.commands import Bot
from database.databasev2 import MATCHING, UserNotFoundException
from time import time

import random

# puts the profile in a queue to be verifed

class NoProfileException(Exception):
    """
    Custom exception raised when a user profile is not found.

    Attributes:
        message (str): Explanation of the error.
    """
    def __init__(self, message="No profile found for the user."):
        self.message = message
        super().__init__(self.message)

class NoCompatibleProfilesError(BaseException):
    def __init__(self, message="Ran out of compatible profiles"):
        self.message = message
        super().__init__(self.message)

class Profile():
    def __init__(self, bot:Bot, data:dict):
        self.bot = bot
        if data == None:
            raise NoProfileException()
        self.id:int = int(data.get('user_id'))
        self.user = bot.get_user(self.id)
        if not self.user: raise UserNotFoundException()
        self.name:str = data.get('name')
        self.pronouns:str = data.get('pronouns')
        self.gender:str = data.get('gender')
        self.age:int = data.get('age', 0)
        self.sexuality:str = data.get('sexuality')
        self.bio:str = data.get('bio')
        self._id = data.get('_id')
        self.approved:bool = data.get('approved')
        self.selected_pairs:list[int] = data.get('selected_pairs', [])
        self.rejected_pairs:list[int] = data.get('rejected_pairs', [])
        self.paired_with_us:list[int] = data.get('paired_with_us', [])
        self.tos:str = data.get('tos_agreed')
        self.profile_message_id:int = data.get('profile_message_id')
        self.profile_channel_id:int = data.get('profile_channel_id')
        self.data:dict = data

    
    def compare(self, other:"Profile") -> bool:
        """compares to profiles to see if they are compatible

        Args:
            other (Profile): the other profile to compare against ours

        Returns:
            bool: True if compatible, false if not
        """
        if self.id == other.id: return False # they arent us
        if not self.approved or not other.approved: return False # both of us must be approved
        if other.id in self.rejected_pairs: return False # we didnt reject them
        if other.id in self.selected_pairs: return False

        our_age = int(self.age)
        their_age = int(other.age)
        
        if our_age -2 > their_age: return False
        if our_age +2 < their_age: return False

        return True

        
        

    def get_compatible_profiles(self) -> list["Profile"]:
        """Generates a list of all compatible profiles for this user

        Returns:
            list[Profile]: a list of profile objects we are compatible with
        """
        approved_profiles = MATCHING.find({'approved':True})
        compatible_profiles = []
        for profile in approved_profiles:
            try:
                other_profile = Profile(self.bot, profile)
            except: continue
            if not self.compare(other_profile): continue
            compatible_profiles.append(other_profile)

        if len(compatible_profiles) == 0:
            raise NoCompatibleProfilesError()
        
        return compatible_profiles
    

    def get_random_profile(self) -> "Profile":
        """randomly grabs a compatible profile

        Returns:
            Profile: a random profile
        """
        compatible_profiles = self.get_compatible_profiles()
        return compatible_profiles[random.randint(0, len(compatible_profiles)-1)]


        

        

    def edit(self, data, upsert=False):
        result = MATCHING.update_one({'_id':self._id}, data, upsert=upsert)
        data = MATCHING.find_one({'_id':self._id})
        self.__init__(self.bot, data)
        return result
    
    def generate_embed(self, color=0xffa1dc):
        description = f"""❥﹒User: {self.user.mention} | `{self.user.global_name}`
❥﹒Name: `{self.name}`
❥﹒Pronouns: `{self.pronouns}`
❥﹒Gender: `{self.gender}`
❥﹒Age: `{self.age}`
❥﹒Sexuality: `{self.sexuality}`
❥﹒Bio:\n```{self.bio}```"""

        profile_embed = Embed(
        title="Profile",
        description=description,
        color=color)
        profile_embed.set_footer(text=f'Profile Id: {self._id}')
        try:
            profile_embed.set_author(name=self.user.global_name, icon_url=self.user.avatar.url)
        except AttributeError: pass # ignore if the user has no pfp

        return profile_embed
    
    def queue_profile(self, message_id:int):
        return self.edit({"$set": {"approved":"waiting", "message_id":message_id,"date":int(time())}})
        
        


def qet_queued(message_id:int, bot) -> Profile:
    """Grabs the queued profile with the provided message_id

    Args:
        message_id (int): the message_id provided
        bot (discord.Bot): discord Bot class to return a profile

    Returns:
        Profile: the profile thats queued
    """
    data = MATCHING.find_one({'message_id':message_id}) or None
    return Profile(bot, data)




def get_profile(user:Member, bot:Bot) -> Profile:
    """Gets a profile with a provided user

    Args:
        user (discord.Member): ther user's profile toget
        bot (Bot): discord.Bot class to check if the user is in the scope of the bot

    Raises:
        UserNotFoundException: Raises if the user is not found

    Returns:
        Profile: the requests profile
    """
    if not user:
        raise UserNotFoundException()
    data = MATCHING.find_one({'user_id':user.id}) or None
    return Profile(bot, data)






