import random


def random_string(length=32):
    choices = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K',\
            'P', 'R', 'S', 'T', 'U', 'V', 'X', 'Y', 'Z', '2', '3',\
            '4', '5', '6', '7', '8', '9']
    code = ''.join(random.choice(choices) for x in range(length))
    return code
