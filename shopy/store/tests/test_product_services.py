
import pytest
from django.core.exceptions import ValidationError

from shopy.store.models import Product
from shopy.store.services.product import product_create


def test_product_create(db):
    data = {'name':  'test', 'retail_price': 100,}
        # 'slug': 'test',

    p = product_create(**data)
    assert p.name == data['name']
    assert p.slug == data['name']

    data['slug'] = 'this-is-a-test'
    p = product_create(**data)
    assert p.slug == 'this-is-a-test'

    assert p.retail_price == data['retail_price']
    assert isinstance(p, Product)

    assert Product.objects.count() == 2

@pytest.mark.parametrize(
    ('name, retail_price'),
    (('', -1),('', 0),('test', 0),('test', -1),(None, None))
)    
def test_product_create_raises_validation_error(db, name, retail_price):
    with pytest.raises(ValidationError):
        product_create(name=name, retail_price=retail_price)


def test_product_create_raises_type_error(db):
    with pytest.raises(TypeError):
        product_create()

    with pytest.raises(TypeError):
        product_create('test', 100)