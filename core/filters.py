import django_filters
from django.forms.widgets import CheckboxSelectMultiple
from .models import Product

class ProductFilter(django_filters.FilterSet):

    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Search')


    # Manually define choices for the category filter
    CATEGORY_CHOICES = [
        ('tools', 'Tools'),
        ('materials', 'Materials'),
        ('electrical', 'Electrical'),
    ]
    
    category = django_filters.MultipleChoiceFilter(
        choices=CATEGORY_CHOICES,  # Manually defined choices
        widget=CheckboxSelectMultiple,
        label='Filter by Category'
    )
    price = django_filters.RangeFilter()

    class Meta:
        model = Product
        fields = ['name', 'category', 'price']

