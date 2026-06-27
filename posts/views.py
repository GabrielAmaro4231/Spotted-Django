from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Post
from .serializers import PostSerializer
from .permissions import IsOwner
from .filters import LeaderboardFilter
from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from .filters import PostFilter
from rest_framework.filters import OrderingFilter


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_at', 'airplane_registration']
    ordering = ['-created_at']
    filterset_class = PostFilter

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[AllowAny],
        authentication_classes=[TokenAuthentication]
    )
    def leaderboard(self, request):
        base_queryset = (
            Post.objects
            .values('user')
            .annotate(post_count=Count('id'))
            .order_by('-post_count', 'user')
        )

        filterset = LeaderboardFilter(request.GET, queryset=base_queryset)

        if not filterset.is_valid():
            return Response(filterset.errors, status=400)

        rankings = filterset.qs

        results = []
        current_user_id = request.user.id if request.user.is_authenticated else None

        for index, entry in enumerate(rankings, start=1):
            user_id = entry['user']

            if current_user_id and user_id == current_user_id:
                name = 'Me'
            else:
                name = f'Anonymous User {index}'

            results.append({
                'position': index,
                'name': name,
                'post_count': entry['post_count']
            })

        return Response(results)
