
SUPPLIER_MAP = {
    'SHEIN': {
        'name': 'SHEIN',
        'keys': {

            'id': 'detail__goods_id',
            'productCode': 'detail__goods_sn',
            'category': 'currentCat__cat_name',
            'name': 'detail__goods_name',
            'cover': 'detail__original_img',
            'sale_price': 'detail__salePrice__amount',
            'retail_price': 'detail__retailPrice__amount',
            'is_on_sale': 'detail__is_on_sale',
            'in_stock': 'detail__is_stock_enough',
        }
    },
    'PLT': {
        'name': 'PLT',
        'keys': {
            'sku': 'sku',
            'name': 'name',
            'description': 'description',
            'cover': 'image',
            'availability': 'offers__availability',
            'attrs__couleur': 'color',
            'cost': 'offers__price',
            'cost_currency': 'offers__priceCurrency',
        }
    },
    'FNOVA': {
        'name': 'FNOVA',
        'keys': {
            'id': 'id',
            'sku': 'sku',
            'name': 'title',
            'category': 'product_type',
            'cover': 'featured_image',
            'handle': 'handle',
            'cost': 'price',
            'attrs': 'tags',
            'imgs': 'media'
        }
    }
}
