import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection


from .models import Printer, Check


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
                obj, created = Check.objects.get_or_create(
                        printer_id=point_printer,
                        check_type=point_printer.check_type,
                        order=order,
                    )
                if created:
                    pass  # TODO добавить в очередь
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

@csrf_exempt
def get_new_checks(request, api_key):
    if request.method == 'GET':
        try:
            printer = Printer.objects.get(api_key=api_key)
        except Printer.DoesNotExist:
            return JsonResponse(
                {'error': 'Ошибка авторизации'},
                status=401,
            )
        checks = printer.checks.filter(status='RE').values('id')

        checks_ids = list(checks)
        print(checks_ids)
        print(len(connection.queries))
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

def create_pdf(check):
    import json
    import requests
    import base64

    url = 'http://localhost:49153/'
    data = {
        'contents': base64.b64encode(bytes(check, 'utf8')).decode('utf-8'),
    }
    headers = {
        'Content-Type': 'application/json',  # This is important
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)

    # Save the response contents to a file
    with open('file.pdf', 'wb') as f:
        f.write(response.content)


def get_pdf(request, api_key, check_id):
    from django.template.loader import render_to_string
    from django.template import Context, Template

    # if request.method == 'GET':
        # if api_key == 'api_key_1' and check_id == 1:
        #     return FileResponse(open('test_pic.png', 'rb'))
    try:
        printer = Printer.objects.get(api_key=api_key)
    except Printer.DoesNotExist:
        return JsonResponse(
            {'error': 'Ошибка авторизации'},
            status=401,
        )
    try:
        check = printer.checks.get(id=check_id)
    except Check.DoesNotExist:
        return JsonResponse(
            {'error': 'Данного чека не существует'},
            status=400,
        )
    templates = {
        'KN': 'kitchen_check.html',
        'CL': 'client_check.html',
    }
    context = check.order
    # page = render(request, templates[check.check_type], context)
    # create_pdf(page.content)
    rendered_check = render_to_string(templates[check.check_type], context)
    create_pdf(rendered_check)
    return HttpResponse('kek')
