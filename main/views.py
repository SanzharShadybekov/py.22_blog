from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from main.models import Category, Post, Comment
from . import serializers
from .permissions import IsAuthor



class StandartResultPagination(PageNumberPagination):
    page_size = 3
    page_query_param = 'page'
    max_page_size = 1000


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    pagination_class = StandartResultPagination
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('title',)
    filterset_fields = ('owner', 'category')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return serializers.PostCreateSerializer
        elif self.action == 'retrieve':
            return serializers.PostSerializer
        else:
            return serializers.PostListSerializer

    def get_permissions(self):
        # Изменять и удалять пост может только автор поста
        if self.action in ('update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsAuthor()]
        # Создавать может залогиненный юзер
        elif self.action == 'create':
            return [permissions.IsAuthenticated()]
        # просматривать могут все
        else:
            return [permissions.AllowAny()]

    # /posts/<id>/comments/
    @action(['GET'], detail=True)
    def comments(self, request, pk):
        post = self.get_object()
        comments = post.comments.all()
        serializer = serializers.CommentSerializer(comments, many=True)
        return Response(serializer.data, status=200)


class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAuthor()]


# class PostListCreateView(generics.ListCreateAPIView):
#     queryset = Post.objects.all()
#     permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
#
#     def get_serializer_class(self):
#         if self.request.method == 'GET':
#             return serializers.PostListSerializer
#         return serializers.PostCreateSerializer
#
#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)
#
#
# class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Post.objects.all()
#
#     def get_permissions(self):
#         if self.request.method in ('PUT', 'PATCH', 'DELETE'):
#             return [permissions.IsAuthenticated(), IsAuthor()]
#         return [permissions.AllowAny()]
#
#     def get_serializer_class(self):
#         if self.request.method in ('PUT', 'PATCH'):
#             return serializers.PostCreateSerializer
#         return serializers.PostSerializer

# function based view
# @api_view(['GET'])
# def category_list(request):
#     queryset = Category.objects.all()
#     serializer = serializers.CategorySerializer(queryset, many=True)
#     return Response(data=serializer.data, status=200)


# class based view (APIview)
# class CategoryListView(APIView):
#     def get(self, request):
#         queryset = Category.objects.all()
#         serializer = serializers.CategorySerializer(queryset, many=True)
#         return Response(serializer.data, status=200)
#
#     def post(self, request):
#         serializer = serializers.CategorySerializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(serializer.data, status=201)

