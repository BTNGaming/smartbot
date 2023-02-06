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
        async def initialize_chain():
            chain = await self.config.chain()
            for text in chain:
                self.chain.add_text(text)
        self.bot.loop.create_task(initialize_chain())
        self.message_counter = 0

        
@commands.command(name="fixbrain")
@checks.is_owner()
async def reset_chain(self, ctx):
    """Reset the Markov chain data."""
    chain_data = await self.config.get_raw("chain")
    # print("Chain data before reset:", chain_data)
    channel = self.bot.get_channel(1068246002731077754) # Replace channel_id with the ID of the channel you want to send messages to
    await channel.send("Chain data before reset:", chain_data)

    self.chain = MarkovChain()
    await self.config.set_raw("chain", value=[])

    chain_data = await self.config.get_raw("chain")
    # print("Chain data after reset:", chain_data)
    channel = self.bot.get_channel(1068246002731077754) # Replace channel_id with the ID of the channel you want to send messages to
    await channel.send("Chain data after reset:", chain_data)

    print(f"{self.bot.user} is listening to {self.bot.event_stats()} events.")
    # await ctx.send("Markov chain data has been reset.")
    channel = self.bot.get_channel(1068246002731077754) # Replace channel_id with the ID of the channel you want to send messages to
    await channel.send("Markov chain data has been reset.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return

        if message.channel.id not in [1067171169687568587, 1068246002731077754]:
            return

        text = message.content.strip()
        self.chain.add_text(text)
        async with self.config.chain.get_lock():
            chain = await self.config.chain()
            chain.append(text)
            await self.config.chain.set(chain)
        
        self.message_counter += 1
        if self.message_counter >= 5 and self.message_counter <= 20:
            generated_message = self.chain.generate_text()
            while not generated_message:
                generated_message = self.chain.generate_text()
            if generated_message:
                await message.channel.send(generated_message)
            self.message_counter = 0


    @commands.command()
    async def speak(self, ctx):
        """Make the bot speak."""
        await ctx.send(self.chain.generate_text())

def setup(bot):
    bot.add_cog(SmartBot(bot))