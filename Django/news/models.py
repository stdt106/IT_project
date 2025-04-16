from django.db import models


class Articles(models.Model):
    title = models.CharField('Название', max_length=50, default="")
    anons = models.CharField('Анонс', max_length=250)
    full_text = models.TextField('Статья')
    date = models.DateTimeField('Дата публикации')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'


class Comments(models.Model):
    article = models.ForeignKey(
        Articles,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Новость'
    )
    content = models.TextField('Комментарий', max_length=500)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'