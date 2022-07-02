from django.contrib import admin

from .models import Printer, Check


@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    pass


@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    pass
