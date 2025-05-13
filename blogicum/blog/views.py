from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import Http404

from .models import Post, Category


class PostListView(ListView):
    model = Post
    paginate_by = 5
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        now = timezone.now()
        return (
            Post.objects
            .filter(
                pub_date__lte=now,
                is_published=True,
                category__is_published=True
            )
            .order_by('-pub_date')[:5]
        )


class CategoryPostListView(ListView):
    model = Post
    template_name = 'blog/category.html'

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')

        category = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )

        return Post.objects.filter(
            category=category,
            is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs.get('category_slug'),
            is_published=True
        )
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        post = get_object_or_404(
            Post,
            pk=self.kwargs.get('id')
        )

        if (
            post.pub_date > timezone.now()
            or not post.is_published
            or not post.category.is_published
        ):
            raise Http404("Публикация недоступна")

        return post
