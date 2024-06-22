from hashids import Hashids

hashids = Hashids(min_length=3, salt="mysecret")  # lenar .env constant


def get_hashed_short_url(value):
    """Возвращает хешированный url адрес."""
    return hashids.encode(value)


def get_decoded_short_url(value):
    """Возвращает декодированный url адрес."""
    return hashids.decode(value)
