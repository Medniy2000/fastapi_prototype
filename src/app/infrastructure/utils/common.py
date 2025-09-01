import string
import random

default_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits


def generate_str(size: int = 6, chars: str = default_chars) -> str:
    return "".join(random.choice(chars) for _ in range(size))
