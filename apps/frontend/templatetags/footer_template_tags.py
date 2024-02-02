from django import template
from apps.store.models import Pages

register = template.Library()

@register.inclusion_tag('frontend/footer_category_pages.html')
def render_footer_pages(category):
    pages = Pages.objects.filter(category=category, is_active=True)
    return {'pages': pages, 'category': category}
