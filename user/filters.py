from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class UserFilter(filters.FilterSet):
    id = NumberInFilter(field_name="id", lookup_expr="in")
    first_name = filters.CharFilter(field_name="first_name", lookup_expr="icontains")
    last_name = filters.CharFilter(field_name="last_name", lookup_expr="icontains")
    date_of_birth = filters.DateFromToRangeFilter(field_name="date_of_birth")

    class Meta:
        model = get_user_model()
        fields = ["id", "first_name", "last_name", "date_of_birth"]
