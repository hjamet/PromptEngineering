from src.levels.level_1 import Level1
from src.levels.level_2 import Level2


def get_level(level_number):
    if level_number == 1:
        return Level1()
    elif level_number == 2:
        return Level2()
    else:
        return Level1()  # Default to Level1 for now


def adjust_score(score):
    return 10 + (score * 0.9)  # 10% minimum + up to 90% based on actual score
