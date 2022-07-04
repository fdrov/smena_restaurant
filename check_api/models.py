from django.db import models

KITCHEN = 'KN'
CLIENT = 'CL'
CHECK_TYPE_CHOICES = [
    (KITCHEN, 'Кухня'),
    (CLIENT, 'Клиент'),
]


class Printer(models.Model):
    name = models.CharField(
        'Название принтера',
        max_length=250,
    )
    api_key = models.CharField(
        'ключ доступа к API',
        max_length=250,
        unique=True,
        help_text='принимает уникальные значения, по нему однозначно определяется принтер',
    )
    check_type = models.CharField(
        'тип чека которые печатает принтер',
        max_length=2,
        choices=CHECK_TYPE_CHOICES,
        default=KITCHEN,
    )
    point_id = models.IntegerField(
        'точка к которой привязан принтер',

    )

    class Meta:
        verbose_name = 'Принтер'
        verbose_name_plural = 'Принтеры'

    def __str__(self):
        return f'{self.name}, {self.check_type}, {self.point_id=}'


class Check(models.Model):
    NEW = 'NW'
    RENDERED = 'RE'
    PRINTED = 'PR'
    STATUS_CHOICES = [
        (NEW, 'Новый'),
        (RENDERED, 'Обработанный'),
        (PRINTED, 'Распечатанный'),
    ]

    printer_id = models.ForeignKey(
        Printer,
        on_delete=models.CASCADE,
        related_name='checks',
    )
    type = models.CharField(
        'тип чека',
        max_length=2,
        choices=CHECK_TYPE_CHOICES,
        default=KITCHEN,
    )
    order = models.JSONField(
        'информация о заказе',

    )
    status = models.CharField(
        'статус чека',
        max_length=2,
        choices=STATUS_CHOICES,
        default=NEW,
    )
    pdf_file = models.FileField(
        'созданный PDF-файл',
        upload_to='pdf/',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Чек'
        verbose_name_plural = 'Чеки'

    def __str__(self):
        return f'{self.pk}, {self.status=}'
