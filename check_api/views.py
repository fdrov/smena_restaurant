import django_rq
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework import status

from django.http import FileResponse

from .models import Printer, Check
from .serializers import OrderSerializer, ApiKeySerializer, GetPdfSerializer
from .tasks import process_pdf


@api_view(['POST'])
def create_checks(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order = serializer.validated_data

    point_id = order.get('point_id')
    point_printers = Printer.objects.filter(point_id=point_id)
    if not point_printers:
        raise ValidationError(
            {'error': 'Для данной точки не настроено ни одного принтера'}
        )
    check_created = []
    for point_printer in point_printers:
        check, created = Check.objects.get_or_create(
                printer_id=point_printer,
                type=point_printer.check_type,
                order=order,
            )
        django_rq.enqueue(process_pdf, check)
        check_created.append(created)
    if not any(check_created):
        raise ValidationError(
            {'error': 'Для данного заказа уже созданы чеки'}
        )
    return Response(
        {'ok': 'Чеки успешно созданы'}
    )


@api_view(['GET'])
def get_new_checks(request, api_key=None):
    if not api_key:
        kwargs_serializer = ApiKeySerializer(data=request.query_params)
        kwargs_serializer.is_valid(raise_exception=True)
        api_key = kwargs_serializer.validated_data.get('api_key')
    try:
        printer = Printer.objects.get(api_key=api_key)
    except Printer.DoesNotExist:
        return Response(
            {'error': 'Ошибка авторизации'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    checks = printer.checks.filter(status=Check.RENDERED).values('id')

    checks_ids = list(checks)
    if checks_ids:
        return Response({'checks': checks_ids})
    return Response(
        {'error': 'Готовых для печати чеков нет'},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(['GET'])
def get_pdf(request, api_key=None, check_id=None):
    if not api_key and not check_id:
        kwargs_serializer = GetPdfSerializer(data=request.query_params)
        kwargs_serializer.is_valid(raise_exception=True)
        api_key = kwargs_serializer.validated_data.get('api_key')
        check_id = kwargs_serializer.validated_data.get('check_id')
    try:
        printer = Printer.objects.get(api_key=api_key)
    except Printer.DoesNotExist:
        return Response(
            {'error': 'Ошибка авторизации'},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    try:
        check = printer.checks.get(id=check_id)
    except Check.DoesNotExist:
        return Response(
            {'error': 'Данного чека не существует'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not check.pdf_file:
        return Response(
            {'error': 'Для данного чека не сгенерирован PDF-файл'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    check.status = Check.PRINTED
    check.save()
    return FileResponse(open(check.pdf_file.path, 'rb'))
