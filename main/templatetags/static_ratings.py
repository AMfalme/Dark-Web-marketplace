from django import template
from decimal import Decimal
from django.template import loader
from django.templatetags.static import static
from .. import app_settings

register = template.Library()


@register.simple_tag(takes_context=True)
def static_ratings(context, value, icon_height=app_settings.STAR_RATINGS_STAR_HEIGHT, icon_width=app_settings.STAR_RATINGS_STAR_WIDTH):
    request = context.get('request')

    user_rating_percentage = 100 * (value / app_settings.STAR_RATINGS_RANGE)

    stars = [i for i in range(1, app_settings.STAR_RATINGS_RANGE + 1)]

    # We get the template to load here rather than using inclusion_tag so that the
    # template name can be passed as a template parameter
    template_name = 'static_rating.html'
    return loader.get_template(template_name).render({
        'rating_value': value,
        'request': request,
        'user_rating_percentage': user_rating_percentage,
        'stars': stars,
        'star_count': app_settings.STAR_RATINGS_RANGE,
        'icon_height': icon_height,
        'icon_width': icon_width,
        'sprite_width': icon_width * 3,
        'sprite_image': static(app_settings.STAR_RATINGS_STAR_SPRITE),
    })
