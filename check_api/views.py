import json

import django_rq

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

from .models import Printer, Check
from .tasks import process_pdf


@csrf_exempt
def create_checks(request):
    if request.method == 'POST':
        order = json.loads(request.body.decode())
        if point_id := order.get('point_id'):
            point_printers = Printer.objects.filter(point_id=point_id)
            if not point_printers:
                return JsonResponse(
                    {'error': 'Для данной точки не настроено ни одного принтера'},
                    status=400,
                )
            check_created = []
            for point_printer in point_printers:
                check, created = Check.objects.get_or_create(
                        printer_id=point_printer,
                        type=point_printer.check_type,
                        order=order,
                    )
                # if created:
                # if not check.pdf_file:
                    # process_pdf(obj)
                django_rq.enqueue(process_pdf, check)
                check_created.append(created)
            if not any(check_created):
                return JsonResponse(
                    {'error': 'Для данного заказа уже созданы чеки'},
                    status=400,
                )
            return JsonResponse(
                {'ok': 'Чеки успешно созданы'},
                status=200,
            )
    return JsonResponse(
        {'error': 'Method Not Allowed'},
        status=405,
    )


def get_new_checks(request, api_key=None):
    if request.method == 'GET':
        if not api_key:
            api_key = request.GET.get('api_key', '')
        try:
            printer = Printer.objects.get(api_key=api_key)
        except Printer.DoesNotExist:
            return JsonResponse(
                {'error': 'Ошибка авторизации'},
                status=401,
            )
        checks = printer.checks.filter(status=Check.RENDERED).values('id')

        checks_ids = list(checks)
        # print(checks_ids)
        # print(len(connection.queries))
        if checks_ids:
            return JsonResponse(

                {'checks': checks_ids},
                status=200,
            )
        return JsonResponse(
            {'error': 'Готовых для печати чеков нет'},
            status=200,
        )
    return JsonResponse(
        {'error': 'Method Not Allowed'},
        status=405,
    )


def get_pdf(request, api_key=None, check_id=None):
    if request.method == 'GET':
        if not api_key and not check_id:
            api_key = request.GET.get('api_key', '')
            check_id = request.GET.get('check_id', '')
        try:
            printer = Printer.objects.get(api_key=api_key)
        except Printer.DoesNotExist:
            return JsonResponse(
                {'error': 'Ошибка авторизации'},
                status=401,
            )
        # print(printer)
        try:
            check = printer.checks.get(id=check_id)
        except Check.DoesNotExist:
            return JsonResponse(
                {'error': 'Данного чека не существует'},
                status=400,
            )
        if not check.pdf_file:
            return JsonResponse(
                {'error': 'Для данного чека не сгенерирован PDF-файл'},
                status=400,
            )
        check.status = Check.PRINTED
        check.save()
        return FileResponse(open(check.pdf_file.path, 'rb'))
    return JsonResponse(
        {'error': 'Method Not Allowed'},
        status=405,
    )