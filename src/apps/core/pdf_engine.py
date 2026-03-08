from __future__ import annotations

from pathlib import Path
from typing import Any

from django.conf import settings
from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject

from .pdf_mapping import build_individual_pdf_field_values


INDIVIDUAL_TEMPLATE = settings.BASE_DIR / "src" / "apps" / "core" / "pdf_templates" / "IndividualForm.pdf"


def _set_need_appearances(writer: PdfWriter) -> None:
    if "/AcroForm" not in writer._root_object:
        return
    writer._root_object["/AcroForm"][NameObject("/NeedAppearances")] = BooleanObject(True)

