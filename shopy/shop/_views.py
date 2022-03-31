import json
from http import HTTPStatus
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from miq.views.generic import TemplateView, DetailView

from .models import Cart, Customer


class CartDetailView(TemplateView):
    template_name = 'orders/cart.django.html'


class OrderCreateView(DetailView):
    model = Cart
    template_name = 'orders/cart.django.html'


class CustomerCreateForm(ModelForm):
    class Meta:
        model = Customer
        fields = ('name', 'phone', 'email')
        error_messages = {
            'name': {'required': _("Veuillez entrer votre nom et prénom."), },
            'phone': {'required': _("Veuillez entrer votre numéro de téléphone."), },
            'email': {'invalid': _("Veuillez entrer une adresse email valide"), },
        }


"""
class CartView(TemplateView):
    model = Lead
    form_class = LeadCreateForm
    template_name = 'orders/cart.django.html'

    def patch(self, *args: tuple, **kwargs: dict):
        slug = self.kwargs.get('slug')
        if not slug:
            return JsonResponse({'cart': 'Required'}, status=HTTPStatus.BAD_REQUEST)

        cart = Cart.objects.filter(slug=slug).first()
        if not cart:
            return JsonResponse({'cart': 'Invalid'}, status=HTTPStatus.BAD_REQUEST)

        data = self.request_to_json()
        action = data.get('action')

        if not action or action not in ['delete', 'update', 'add']:
            return JsonResponse({'action': 'Invalid'}, status=HTTPStatus.BAD_REQUEST)

        item_slug = data.get('slug', '')
        size = data.get('size')

        if action == 'add' and (prod := Product.objects.filter(meta_slug=item_slug).first()):
            cart.products.add(prod, through_defaults={'size': size})
            # return JsonResponse(cart_to_dict(cart), status=HTTPStatus.OK)

        item = cart.items.filter(slug=item_slug).first()
        if not item:
            return JsonResponse({'item': 'Invalid'}, status=HTTPStatus.BAD_REQUEST)

        if action == 'delete':
            item.delete()

        if action == 'update':
            cart.update_size(item_slug, size)

        # return JsonResponse(cart_to_dict(cart), status=HTTPStatus.OK)

    def post(self, request: 'http.HttpRequest', *args, **kwargs) -> 'JsonResponse':

        session = self.get_session()
        form_data = self.request_to_json()

        lead = None
        lid = session.get('LID', None)
        if lid:
            lead = Lead.objects.filter(slug=lid).first()

        if not lead:
            form = self.form_class(data=form_data)
            if not form.is_valid():
                errors = self.form_errors_to_json(form)
                # return JsonResponse(errors, status=HTTPStatus.BAD_REQUEST)

            lead = form.save()
            session['LID'] = f'{lead.slug}'
            session.modified = True

        cart = None
        cid = session.get('CID', None)
        if cid:
            cart = Cart.objects.filter(slug=cid).first()

        if not cart:
            cart = Cart.objects.create(lead=lead)
            session['CID'] = f'{cart.slug}'
            session.modified = True

        if (prod_slug := form_data.get('product')) and (prod := Product.objects.filter(meta_slug=prod_slug).first()):
            cart.products.add(
                prod, through_defaults={'size': form_data.get('size', '')})

        # return JsonResponse(cart_to_dict(cart), status=HTTPStatus.CREATED)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        if self.request.method != "GET":
            return ctx

        data = {}
        # if cart := self.get_cart_items():
        #     data['cart'] = cart

        self.update_sharedData(ctx, data)
        return ctx

    def form_errors_to_json(self, form):
        errors = form.errors.get_json_data(escape_html=False)
        self.errors = errors.get('__all__')
        return errors

    def request_to_json(self):
        try:
            return json.loads(self.request.body)
        except Exception:
            return {}
"""
