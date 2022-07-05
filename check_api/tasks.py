import json
import base64
from pathlib import Path

import requests

from django.template.loader import render_to_string
from django.conf import settings
from django.core.files.base import ContentFile

from check_api.models import Check

WKHTMLTOPDF = settings.WKHTMLTOPDF


def generate_pdf_file(check):
    url = f'http://{WKHTMLTOPDF["HOST"]}:{WKHTMLTOPDF["PORT"]}'
    data = {
        'contents': base64.b64encode(bytes(check, 'utf8')).decode('utf-8'),
    }
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)

    return response.content


def mark_as_rendered(obj):
    obj.status = Check.RENDERED
    obj.save()
    return


def process_pdf(check):
    templates = {
        'KN': 'kitchen_check.html',
        'CL': 'client_check.html',
    }
    check_type_names = {
        'KN': 'kitchen',
        'CL': 'client',
    }

    file_name = f'{check.order["id"]}_{check_type_names[check.type]}.pdf'
    path = Path(settings.MEDIA_ROOT / 'pdf' / file_name)
    if path.is_file():
        check.pdf_file = str(Path('pdf') / file_name)
        mark_as_rendered(check)
        return

    rendered_check = render_to_string(templates[check.type], context=check.order)
    pdf_check = generate_pdf_file(rendered_check)

    check.pdf_file.save(file_name, ContentFile(pdf_check), save=False)
    mark_as_rendered(check)
    return
