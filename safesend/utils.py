import random
import string

chars = string.ascii_letters + string.digits + string.punctuation


def password_generator():
    return "".join(map(lambda x: random.choice(chars), range(random.randint(10, 15))))
