
from django.db import models
from django.urls import reverse_lazy
from django.utils.text import capfirst
from django.utils.text import Truncator

from ..sales.api import APIImageSerializer


def get_category_url(cat: 'models.Model') -> str:
    if cat.get_is_public():
        return reverse_lazy('shopy:category', args=[cat.meta_slug])
    return ''


def category_to_dict(cat: 'models.Model') -> dict:
    return {
        'name': capfirst(cat.name),
        'name_truncated': capfirst(Truncator(cat.name).chars(30)),
        'meta_slug': cat.meta_slug,
        'url': get_category_url(cat),
        'cover': APIImageSerializer(cat.cover).data,
        'description': cat.description,
    }
