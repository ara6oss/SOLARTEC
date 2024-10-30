from django.db import models

class Client(models.Model):
    phone_number = models.CharField(max_length=15, unique=True, verbose_name="Номер телефона")
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Имя клиента")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"{self.name} ({self.phone_number})"


class Notification(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Текст'),
        ('file', 'Файл'),
        ('location', 'Локация'),
    ]

    MESSAGE_DIRECTION_CHOICES = [
        ('incoming', 'Входящее'),
        ('outgoing', 'Исходящее'),
    ]

    client = models.ForeignKey(Client, related_name='messages', on_delete=models.CASCADE, verbose_name="Клиент")
    message_type = models.CharField(max_length=50, choices=MESSAGE_TYPE_CHOICES, default='text', verbose_name="Тип сообщения")
    direction = models.CharField(max_length=50, choices=MESSAGE_DIRECTION_CHOICES, default='outgoing', verbose_name="Направление сообщения")
    content = models.TextField(verbose_name="Содержимое сообщения")
    status = models.CharField(max_length=50, choices=[
        ('sent', 'Отправлено'),
        ('delivered', 'Доставлено'),
        ('failed', 'Не доставлено'),
    ], default='sent', verbose_name="Статус сообщения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    received_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата получения")

    def __str__(self):
        return f"{self.get_direction_display()} message to/from {self.client.phone_number} - Status: {self.status}"
