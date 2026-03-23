from __future__ import annotations

from pathlib import Path
from typing import Any

from django.conf import settings
from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject, TextStringObject

from .pdf_mapping import build_business_pdf_field_values, build_individual_pdf_field_values


BUSINESS_TEMPLATE = settings.BASE_DIR / "src" / "apps" / "core" / "pdf_templates" / "BusinessForm.pdf"
INDIVIDUAL_TEMPLATE = settings.BASE_DIR / "src" / "apps" / "core" / "pdf_templates" / "IndividualForm.pdf"


def _prepare_acroform(writer: PdfWriter, reader: PdfReader) -> None:
    root = reader.trailer.get("/Root", {})
    acroform = root.get("/AcroForm")
    if acroform:
        writer._root_object.update({NameObject("/AcroForm"): acroform})

    # pypdf helper for NeedAppearances (API differs by version).
    if hasattr(writer, "set_need_appearances_writer"):
        try:
            writer.set_need_appearances_writer(True)
        except TypeError:
            writer.set_need_appearances_writer()

    _set_need_appearances(writer)
    _ensure_default_appearance(writer)


def _set_need_appearances(writer: PdfWriter) -> None:
    if "/AcroForm" not in writer._root_object:
        return
    writer._root_object["/AcroForm"][NameObject("/NeedAppearances")] = BooleanObject(True)


def _ensure_default_appearance(writer: PdfWriter) -> None:
    if "/AcroForm" not in writer._root_object:
        return

    acroform = writer._root_object["/AcroForm"]
    if "/DA" not in acroform:
        # Default appearance: Helvetica, auto size, black.
        acroform[NameObject("/DA")] = TextStringObject("/Helv 0 Tf 0 g")


def fill_individual_pdf(
    cleaned_data: dict[str, Any],
    *,
    output_path: Path,
    template_path: Path = INDIVIDUAL_TEMPLATE,
) -> Path:
    field_values = build_individual_pdf_field_values(cleaned_data)
    return _fill_pdf(field_values, output_path=output_path, template_path=template_path)


def fill_business_pdf(
    cleaned_data: dict[str, Any],
    *,
    output_path: Path,
    template_path: Path = BUSINESS_TEMPLATE,
) -> Path:
    field_values = build_business_pdf_field_values(cleaned_data)
    return _fill_pdf(field_values, output_path=output_path, template_path=template_path)


def _fill_pdf(
    field_values: dict[str, str],
    *,
    output_path: Path,
    template_path: Path,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(template_path))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    _prepare_acroform(writer, reader)

    for page in writer.pages:
        writer.update_page_form_field_values(
            page,
            field_values,
            auto_regenerate=True,
        )

    with output_path.open("wb") as output_file:
        writer.write(output_file)

    return output_path
