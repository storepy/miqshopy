import json

from django.utils.text import capfirst
from django.utils.text import Truncator
from django.utils.safestring import mark_safe
from django.contrib.sites.shortcuts import get_current_site

import miq.core
import shopy

from shopy.store.utils import intcomma
from shopy.store.models import Category


# https://www.facebook.com/business/help/120325381656392?id=725943027795860


def get_published_categories():
    return Category.objects.published()\
        .has_products().order_by('position', 'created')


def product_to_jsonld(product: 'shopy.models.Product', request) -> str:
    site = get_current_site(request)
    url = product.path(request=request)
    info = {
        "@context": "http://schema.org", "@type": "Product",
        "brand": brand_to_jsonld(request, site),
        "productID": Truncator(product.meta_slug).chars(100),
        "name": capfirst(Truncator(product.name).chars(150)),
        "url": url,
    }

    if (description := product.description):
        info["description"] = Truncator(description).chars(9999) or ''

    if cat := product.category:
        info["category"] = capfirst(cat.name)

    if cover := product.cover:
        info["image"] = [img_to_jsonld(request, cover)]

    if (images := product.images) and images.exists():
        imgs = info.get('image', [])
        imgs.extend([img_to_jsonld(request, img) for img in images.all()[:20]])

    if (color := product.attributes.filter(name='color')) and color.exists():
        info["color"] = color.first().value

    # TODO
    currency = "XOF"
    price = f'{intcomma(int(product.get_price()))}'

    if product.is_on_sale:
        price = f"{intcomma(int(product.sale_price))}"

    info["offers"] = {
        "@type": "Offer",
        "priceCurrency": currency,
        "price": price,
        "url": url,
        "itemCondition": "http://schema.org/NewCondition",
        "availability": "http://schema.org/InStock",
        "seller": brand_to_jsonld(request, site)
    }

    return mark_safe(json.dumps(info))


def brand_to_jsonld(request, site, *, is_dict: bool = True):
    data = {
        "@context": "http://schema.org", "@type": "Brand",
        "name": capfirst(site.name),
        # TODO: can be spoofed
        "url": request.get_host()
    }
    if (hasattr(site, 'settings')) and (setting := site.settings):
        if (logo := setting.logo):
            data['logo'] = img_to_jsonld(request, logo)

    if not is_dict:
        return mark_safe(json.dumps(data))
    return data


def img_to_jsonld(request, img: 'miq.core.models.Image', *, is_dict: bool = True):
    src = img.src
    data = {
        "@context": "http://schema.org", "@type": "ImageObject",
        'caption': img.caption or '',
        'contentUrl': request.build_absolute_uri(src.url),
        'width': src.width,
        'height': src.height,
    }

    if not is_dict:
        return mark_safe(json.dumps(data))
    return data
