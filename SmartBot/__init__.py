from .smartbot import SmartBot


def setup(bot):
    bot.add_cog(SmartBot(bot))