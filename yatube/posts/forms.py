from django.forms import ModelForm, Textarea
from django.forms.widgets import Select, ClearableFileInput
from posts.models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image',)
        widgets = {
            'text': Textarea(attrs={'class': 'form-control'}),
            'group': Select(attrs={'class': 'form-control'}),
            'image': ClearableFileInput(attrs={'class': 'form-control'})
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': Textarea(attrs={'class': 'form-control'}),
        }
