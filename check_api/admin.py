from django.contrib import admin

from .models import Printer, Check


@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    list_display = ['name', 'check_type', 'point_id']


@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = ['pk', 'status', 'printer_id', 'type']

