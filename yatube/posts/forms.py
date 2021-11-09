from django.forms import ModelForm

from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'text': 'Текст поста',
            'group': 'Сообщество'}
        help_text = {
            'text': 'Hапишите свой пост здесь',
            'group': 'Выберите сообщество'}
