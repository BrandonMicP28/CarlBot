from discord.ext import commands


class Wordle:
    def __init__(self, max_guesses: int):
        self.max_guesses = max_guesses