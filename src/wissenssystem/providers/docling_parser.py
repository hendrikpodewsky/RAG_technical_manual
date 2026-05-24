import io
from pathlib import Path

from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
)
from docling.document_converter import DocumentConverter
from docling_core.types.doc import (
    DocItemLabel,
    PictureItem,
    SectionHeaderItem,
    TableItem,
    TextItem,
)

from wissenssystem.interfaces.document_parser import ParsedBlock


def _build_converter() -> DocumentConverter:
    options = PdfPipelineOptions(
        do_table_structure=True,
        generate_picture_images=True,
        generate_page_images=False,
        accelerator_options=AcceleratorOptions(device=AcceleratorDevice.CPU),
    )
    from docling.document_converter import PdfFormatOption

    return DocumentConverter(
        format_options={
            __import__(
                "docling.datamodel.base_models", fromlist=["InputFormat"]
            ).InputFormat.PDF: PdfFormatOption(pipeline_options=options)
        }
    )


class DoclingParserAdapter:
    """DocumentParser backed by Docling, preserving table integrity and extracting images."""

    def __init__(self) -> None:
        self._converter = _build_converter()

    def parse(self, pdf_path: Path) -> list[ParsedBlock]:
        result = self._converter.convert(str(pdf_path))
        doc = result.document
        blocks: list[ParsedBlock] = []
        section_path: list[str] = []

        for item, level in doc.iterate_items():
            prov = item.prov[0] if item.prov else None
            page = prov.page_no if prov else 0
            position = (
                {
                    "l": prov.bbox.l,
                    "t": prov.bbox.t,
                    "r": prov.bbox.r,
                    "b": prov.bbox.b,
                }
                if prov and prov.bbox
                else None
            )

            if isinstance(item, SectionHeaderItem):
                _update_section_path(section_path, item.text, level)
                blocks.append(
                    ParsedBlock(
                        block_type="heading",
                        content=item.text,
                        page=page,
                        level=level,
                        position=position,
                        section_path=list(section_path),
                        image_data=None,
                        image_media_type=None,
                    )
                )

            elif isinstance(item, TableItem):
                content = item.export_to_markdown(doc)
                blocks.append(
                    ParsedBlock(
                        block_type="table",
                        content=content,
                        page=page,
                        level=None,
                        position=position,
                        section_path=list(section_path),
                        image_data=None,
                        image_media_type=None,
                    )
                )

            elif isinstance(item, PictureItem):
                image_data, media_type = _extract_image_bytes(item, doc)
                caption = item.caption_text(doc) or ""
                blocks.append(
                    ParsedBlock(
                        block_type="image",
                        content=caption,
                        page=page,
                        level=None,
                        position=position,
                        section_path=list(section_path),
                        image_data=image_data,
                        image_media_type=media_type if image_data else None,
                    )
                )

            elif isinstance(item, TextItem) and item.label in (
                DocItemLabel.TEXT,
                DocItemLabel.PARAGRAPH,
                DocItemLabel.LIST_ITEM,
                DocItemLabel.TITLE,
                DocItemLabel.FOOTNOTE,
            ):
                if item.text.strip():
                    blocks.append(
                        ParsedBlock(
                            block_type="text",
                            content=item.text,
                            page=page,
                            level=None,
                            position=position,
                            section_path=list(section_path),
                            image_data=None,
                            image_media_type=None,
                        )
                    )

        return blocks


def _update_section_path(section_path: list[str], heading: str, level: int) -> None:
    """Maintain running section path based on heading depth (level 0 = top-level)."""
    target_depth = level + 1
    if len(section_path) >= target_depth:
        del section_path[target_depth - 1 :]
    while len(section_path) < target_depth - 1:
        section_path.append("")
    section_path.append(heading)


def _extract_image_bytes(item: PictureItem, doc) -> tuple[bytes | None, str]:
    try:
        pil_image = item.get_image(doc)
        if pil_image is None:
            return None, ""
        buf = io.BytesIO()
        fmt = pil_image.format or "PNG"
        pil_image.save(buf, format=fmt)
        mime = f"image/{fmt.lower()}"
        return buf.getvalue(), mime
    except Exception:
        return None, ""
