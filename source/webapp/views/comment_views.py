from django.shortcuts import render, get_object_or_404, redirect
from webapp.forms import CommentForm
from webapp.models import Comment
from django.views import View
from django.views.generic import TemplateView
from .base_views import ListView
class CommentIndexView(ListView):
    template_name = 'comment/index_coment.html'
    model = Comment
    context_key = 'comments'

class CommentView(TemplateView):
    template_name = 'comment/comment.html'

    def get_context_data(self, **kwargs):
        pk = kwargs.get('pk')
        context = super().get_context_data(**kwargs)
        context['comment'] = get_object_or_404(Comment, pk=pk)
        return context




class CommentUpdateView(View):
    def get(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs.get('pk'))
        form = CommentForm(data={
            'article': comment.article,
            'author': comment.author,
            'text': comment.text
        })
        return render(request, 'comment/update.html', context={'form': form, 'comment': comment})

    def post(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs.get('pk'))
        form = CommentForm(data=request.POST)
        if form.is_valid():
            comment.article = form.cleaned_data['article']
            comment.author = form.cleaned_data['author']
            comment.text = form.cleaned_data['text']
            comment.save()
            return redirect('comment_view', pk=comment.pk)
        else:
            return render(request, 'comment/update.html', context={'form': form, 'comment': comment})


class CommentDeleteView(View):
    def get(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs.get('pk'))
        return render(request, 'comment/delete.html', context={'comment': comment})

    def post(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs.get('pk'))
        comment.delete()
        return redirect('comment_index')


class CommentCreateView(View):
    def get(self, request, *args, **kwargs):
        form = CommentForm()
        return render(request, 'comment/create.html', context={'form': form})

    def post(self, request, *args, **kwargs):
        form = CommentForm(data=request.POST)
        if form.is_valid():
            comment = Comment.objects.create(
                author=form.cleaned_data['author'],
                text=form.cleaned_data['text'],
                article=form.cleaned_data['article']
            )
            # это нужно исправить на ваш url.
            return redirect('comment_view', pk=comment.pk)
        else:
            return render(request, 'comment/create.html', context={'form': form})