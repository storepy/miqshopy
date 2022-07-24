import logging

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _

from miq.core.models import BaseModelMixin

from .managers import CustomerManager


logger = logging.getLogger(__name__)
User = get_user_model()


class CustomerUser(User):
    class Meta:
        proxy = True


class Customer(BaseModelMixin):
    user = models.OneToOneField(
        CustomerUser, related_name='customer',
        null=True, blank=True,
        on_delete=models.PROTECT
    )

    added_by = models.ForeignKey(
        'staff.User', related_name='added_customers',
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    first_name = models.CharField(
        _('First name'), max_length=100,
        blank=True, null=True,
        validators=[
            MinLengthValidator(2, message=_('Enter your first name.'))
        ])
    last_name = models.CharField(
        _('Last name'), max_length=100,
        blank=True, null=True,
        validators=[MinLengthValidator(2, message=_('Enter your last name.'))])

    phone = models.CharField(
        _("Phone Number"), max_length=50, unique=True,
        validators=[
            MinLengthValidator(4, message=_("Veuillez entrer votre numéro de téléphone."))]
    )

    email = models.EmailField(unique=True, null=True, blank=True)

    objects = CustomerManager()

    def save(self, *args, **kwargs):
        if self.email == '':
            self.email = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username if self.user else self.phone

    class Meta:
        ordering = ('-created',)
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')
