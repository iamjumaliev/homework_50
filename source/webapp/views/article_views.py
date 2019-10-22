from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode
from django.views.generic import ListView, DetailView, CreateView, \
    UpdateView, DeleteView, FormView

from webapp.forms import ArticleForm, ArticleCommentForm, SimpleSearchForm, FullSearchForm
from webapp.models import Article, Tag
from django.core.paginator import Paginator


class IndexView(ListView):
    template_name = 'Article/index.html'
    context_object_name = 'articles'
    model = Article
    ordering = ['-created_at']
    paginate_by = 5
    paginate_orphans = 1

    def get(self, request, *args, **kwargs):
        self.form = self.get_search_form()
        self.search_value = self.get_search_value()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.search_value:
            print(self.search_value)
            print(queryset.filter(tags__name__icontains=self.search_value).values('tags__name'))
            queryset = queryset.filter(
                Q(title__icontains=self.search_value)
                | Q(author__icontains=self.search_value)
                | Q(tags__name__iexact=self.search_value)
            ).distinct()
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['form'] = self.form
        if self.search_value:
            context['query'] = urlencode({'tag': self.search_value})
        context['archived_articles'] = self.get_archived_articles()
        return context

    def get_archived_articles(self):
        queryset = super().get_queryset()
        return queryset

    def get_search_form(self):
        return SimpleSearchForm(data=self.request.GET)

    def get_search_value(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search']
        return None


class ArticleView(DetailView):
    template_name = 'Article/article.html'
    model = Article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        context['form'] = ArticleCommentForm()
        print(article.tags.all())
        comments = article.comments.order_by('-created_at')
        self.paginate_comments_to_context(comments, context)
        return context

    def paginate_comments_to_context(self, comments, context):
        paginator = Paginator(comments, 3, 0)
        page_number = self.request.GET.get('page', 1)
        page = paginator.get_page(page_number)
        context['paginator'] = paginator
        context['page_obj'] = page
        context['comments'] = page.object_list
        context['is_paginated'] = page.has_other_pages()



class ArticleCreateView(CreateView):
    form_class = ArticleForm
    model = Article
    template_name = 'Article/create.html'

    def get_success_url(self):
        return reverse('article_view', kwargs={'pk': self.object.pk})


    def form_valid(self, form):
        self.object = form.save()
        self.tag_parser()
        return redirect(self.get_success_url())

    def tag_parser(self):
        tags = self.request.POST.get('tags')
        tag_list = tags.split(',')
        for tag in tag_list:
            given_tag, created =Tag.objects.get_or_create(name=tag)
            self.object.tags.add(given_tag)



class ArticleUpdateView(UpdateView):
    model = Article
    template_name = 'Article/update.html'
    form_class = ArticleForm
    context_object_name = 'article'

    def get_success_url(self):
        return reverse('article_view', kwargs={'pk': self.object.pk})

    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        tag_list = ''
        tags = list(self.object.tags.all())
        for tag in tags:
                tag_list += tag.name + ','
        form.fields['tags'].initial = tag_list.strip()
        return form



    def form_valid(self, form):
        self.object = form.save()
        self.tag_parser()
        return redirect(self.get_success_url())

    def tag_parser(self):
        tags = self.request.POST.get('tags')
        tag_list = tags.split(',')
        self.object.tags.clear()
        for tag in tag_list:
            given_tag, created =Tag.objects.get_or_create(name=tag)
            self.object.tags.add(given_tag)


class ArticleDeleteView(DeleteView):
    model = Article
    template_name = 'Article/delete.html'
    context_object_name = 'article'
    success_url = reverse_lazy('index')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.save()
        return redirect(self.get_success_url())


class ArticleSearchView(FormView):
    template_name = 'Article/search.html'
    form_class = FullSearchForm

    def form_valid(self, form):
        text = form.cleaned_data.get('text')
        author = form.cleaned_data.get('author')

        query = (self.get_text_search_query(form, text) & self.get_author_search_query(form,author))
        context = self.get_context_data(form=form)
        context['articles'] = Article.objects.filter(query).distinct()
        return self.render_to_response(context=context)

    def get_text_search_query(self, form, text):
        query = Q()
        if text:
            in_title = form.cleaned_data.get('in_title')
            if in_title:
                query = query | Q(title__icontains=text)
            in_text = form.cleaned_data.get('in_text')
            if in_text:
                query = query | Q(text__icontains=text)
            in_tags = form.cleaned_data.get('in_tags')
            if in_tags:
                query = query | Q(tags__name__iexact=text)
            in_comment_text = form.cleaned_data.get('in_comment_text')
            if in_comment_text:
                query = query | Q(comments__text__icontains=text)
        return query

    def get_author_search_query(self,form,author):
        query = Q()
        if author:
            in_articles = form.cleaned_data.get('in_articles')
            if in_articles:
                query = query | Q(author__iexact=author)
            in_comments = form.cleaned_data.get('in_comments')
            if in_comments:
                query = query | Q(comments__author__iexact=author)
        return query