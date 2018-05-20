from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, reverse
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Cart, CartItem
from .forms import CouponForm
from products.models import Product
import random
from string import ascii_letters


def generate_cart_id():
    new_id = ''
    for i in range(50):
        new_id = new_id + random.choice(ascii_letters)
    return new_id


def check_if_cart_id(request):
    try:
        cart_id = request.session['cart_id']
    except:
        request.session['cart_id'] = generate_cart_id()
    return request.session['cart_id']


def check_or_create_cart(request):
    user = request.user
    card_id = check_if_cart_id(request)
    cart_order_exists = Cart.my_query.active_carts().filter(id_session=card_id,
                                                            active=True,
                                                            )
    if not cart_order_exists:
        cart = Cart.objects.create(id_session=card_id)
        if user.is_authenticated:
            cart.user = user
            cart.save()
    else:
        cart = cart_order_exists.last()
    return cart


def cart_data(request):
    session_id = check_if_cart_id(request)
    try:
        cart = Cart.objects.filter(id_session=session_id).last()
        cart_items = cart.cartitem_set.all() if cart else None
    except:
        cart, cart_items = None, None
    return [cart, cart_items]


def add_to_cart(request, dk, qty=1):
    instance = get_object_or_404(Product, id=dk)
    order = check_or_create_cart(request)
    CartItem.create_cart_item(request, order=order, product=instance, qty=qty)
    messages.success(request, ' The product %s added to cart' % instance.title)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def delete_cart_item(request, dk):
    object = get_object_or_404(CartItem, id=dk)
    messages.warning(request, 'The product %s has deleted' % object.product_related.title)
    object.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def create_coupon(request):
    form = CouponForm(request.POST or None)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('dashboard:settings_page'))
    form_title = 'Create Coupon'
    context = locals()
    return render(request, 'dashboard/form_view.html', context)