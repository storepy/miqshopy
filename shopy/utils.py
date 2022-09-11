import logging

from django.contrib.sites.models import Site

from miq.core.middleware import local


_shared_ = {}
logger = logging.getLogger(__name__)


def get_currency() -> str:
    if 'currency' not in _shared_:
        _shared_['currency'] = get_store_settings().currency  # type: str
        logger.info(f'Retrieved store currency[{_shared_["currency"]}]')
    return _shared_['currency']


def get_store_settings():
    if 'store_settings' not in _shared_ or not _shared_['store_settings']:
        from .store.models import ShopSetting
        site: Site = getattr(local, 'site', Site.objects.get_current())
        settings = ShopSetting.objects.filter(site_id=site.id).first()
        _shared_['store_settings'] = settings
        logger.info(f'Retrieved site[{site.id}] store setting[{settings.id}]')
    return _shared_['store_settings']
