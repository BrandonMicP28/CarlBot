import math

from utils.database import User


def get_level(user: User):
    xp = user.experience
    for level in range(1001):
        if level_to_xp(level + 1) > xp:
            return level
    return 1000

def level_to_xp(level: int):
    xp: int = math.floor(0.8 * math.pow(level, 3) +
                      60 * math.pow(level, 2) +
                      100 * level)
    return xp
