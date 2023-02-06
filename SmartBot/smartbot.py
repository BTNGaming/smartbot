import os
import random
from collections import defaultdict

import redbot.core
from redbot.core import Config, checks, commands

class MarkovChain:
    def __init__(self):
        self.data = defaultdict(list)

    def add_text(self, text):
        words = text.split()
        for i, word in enumerate(words[:-1]):
            next_word = words[i + 1]
            self.data[word].append(next_word)

    def generate_text(self, length=15):
        current_word = random.choice(list(self.data.keys()))
        result = current_word
        for i in range(length - 1):
            next_word = random.choice(self.data[current_word])
            result += " " + next_word
            current_word = next_word
        return result

class SmartBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=114514)
        default_global = {"chain": []}
        self.config.register_global(**default_global)

        self.chain = MarkovChain()
        for text in self.config.chain():
            self.chain.add_text(text)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return

        text = message.content.strip()
        self.chain.add_text(text)
        async with self.config.chain.get_lock():
            chain = self.config.chain()
            chain.append(text)
            await self.config.chain.set(chain)

    @commands.command()
    async def speak(self, ctx):
        """Make the bot speak."""
        await ctx.send(self.chain.generate_text())

def setup(bot):
    bot.add_cog(SmartBot(bot))