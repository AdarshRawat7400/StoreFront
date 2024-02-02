from django import template
from apps.store.models import Order, OrderItem
from django.utils import timezone

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(customer=user, ordered=False)
        if qs.exists():
            return qs[0].items.count()
    return 0
