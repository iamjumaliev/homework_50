from django import forms

from webapp.models import  Article, Comment


class ArticleForm(forms.ModelForm):

    tags = forms.CharField(max_length=100,required=False,label='Тэг')

    class Meta:
        model = Article
        exclude = ['created_at', 'updated_at','tags']


class CommentForm(forms.ModelForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    class Meta:
        model = Comment
        exclude = ['created_at', 'updated_at']


class ArticleCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author', 'text']


class SimpleSearchForm(forms.Form):
    tag = forms.CharField(max_length=100, required=False, label='Найти')