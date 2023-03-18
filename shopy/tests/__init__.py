import random
from django.utils.crypto import get_random_string


def get_random_product_data():
    return {
        'name': get_random_string(length=32),
        'slug': get_random_string(length=32),
        'retail_price': random.randint(1, 100),
    }
