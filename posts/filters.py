import django_filters
from .models import Post


class LeaderboardFilter(django_filters.FilterSet):
    ordering = django_filters.CharFilter(method='filter_ordering')

    def filter_ordering(self, queryset, name, value):
        if value == 'asc':
            return queryset.order_by('post_count', 'user')
        elif value == 'desc':
            return queryset.order_by('-post_count', 'user')
        return queryset
    

class PostFilter(django_filters.FilterSet):
    airplane_registration = django_filters.CharFilter(lookup_expr='icontains')
    airplane_model = django_filters.CharFilter(lookup_expr='icontains')
    airline = django_filters.CharFilter(lookup_expr='icontains')

    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte'
    )

    class Meta:
        model = Post
        fields = [
            'airplane_registration',
            'airplane_model',
            'airline',
        ]