import os
import django

from django.db import connection
from django.template import Context, Template


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "check_generator.settings")
django.setup()

# import models AFTER DJANGO SETTINGS INIT!
from check_api.models import *


import json
import base64
from pathlib import Path

import requests

from django.template.loader import render_to_string
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile

from check_api.models import Check

WKHTMLTOPDF = settings.WKHTMLTOPDF

# def render_html(template, order):
#     templates = {
#         'KN': 'kitchen_check.html',
#         'CL': 'client_check.html',
#     }
#     return render_to_string(templates, order)


def generate_pdf_file(check, filename):
    url = f'http://{WKHTMLTOPDF["HOST"]}:{WKHTMLTOPDF["PORT"]}'
    data = {
        'contents': base64.b64encode(bytes(check, 'utf8')).decode('utf-8'),
    }
    headers = {
        'Content-Type': 'application/json',  # This is important
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)

    return response.content
    # with open(filename, 'wb') as f:
    #     f.write(response.content)


def process_pdf(check):
    templates = {
        'KN': 'kitchen_check.html',
        'CL': 'client_check.html',
    }


    file_name = f'{check.order["id"]}_{check.type}.pdf'

    path = Path(settings.MEDIA_ROOT / 'pdf' / file_name)
    if path.is_file():
        return

    rendered_check = render_to_string(templates[check.type], context=check.order)

    file = ContentFile(generate_pdf_file(rendered_check, file_name))
    # check.pdf_file = str(path)
    check.pdf_file.save(file_name, file, save=False)
    check.status = 'RE'
    check.save()
