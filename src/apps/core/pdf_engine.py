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


def fill_individual_pdf(
    cleaned_data: dict[str, Any],
    *,
    output_path: Path,
    template_path: Path = INDIVIDUAL_TEMPLATE,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(template_path))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    if reader.trailer.get("/Root", {}).get("/AcroForm"):
        writer._root_object.update(
            {NameObject("/AcroForm"): reader.trailer["/Root"]["/AcroForm"]}
        )

    field_values = build_individual_pdf_field_values(cleaned_data)
    for page in writer.pages:
        writer.update_page_form_field_values(
            page,
            field_values,
            auto_regenerate=False,
        )

    _set_need_appearances(writer)

    with output_path.open("wb") as output_file:
        writer.write(output_file)

    return output_path
