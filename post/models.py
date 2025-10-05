from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator, MaxLengthValidator
from django.db import models
from django.db.models import UniqueConstraint

from shared.models import BaseModels
Users=get_user_model()

class Post(BaseModels):
    author=models.ForeignKey(Users,on_delete=models.CASCADE,related_name='posts')
    image=models.ImageField(
        upload_to='post_photo/',
        validators=[FileExtensionValidator(
        allowed_extensions=['jpg',
                            'jpeg',
                            'png'
                            ]
        )
    ])
    caption=models.TextField(validators=[MaxLengthValidator(2000)])
    class Meta:
        db_table='posts'
        verbose_name='post'
        verbose_name_plural='posts'
    def __str__(self):
        return f'{self.author} about  {self.caption}'
class PostComment(BaseModels):
    author=models.ForeignKey(Users,on_delete=models.CASCADE)
    post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
    comment=models.TextField()
    parent=models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name='child',
        null=True,
        blank=True,
    )
    def __str__(self):
        return f"comment by {self.author}"

class PostLike(BaseModels):
    author = models.ForeignKey(Users, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['author', 'post'], name='PostLikeUnique')
        ]



class CommentLike(BaseModels):
    author = models.ForeignKey(Users, on_delete=models.CASCADE)
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['author', 'comment'], name='CommentLikeUnique')
        ]

    def __str__(self):
        return f'{self.author} {self.comment}'



