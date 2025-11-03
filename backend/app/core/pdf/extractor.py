"""
PDF extractor service using camelot-py and PyMuPDF for hybrid extraction.

Extracts both structured tables and text from PDFs, with support for
MinIO object storage streams.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import io
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract text and tables from PDF documents using hybrid approach."""

    def __init__(self):
        """Initialize PDF extractor."""
        self._camelot_available = False
        self._fitz_available = False
        self._pdfplumber_available = False

        # Check available libraries
        try:
            import camelot  # noqa: F401

            self._camelot_available = True
            logger.info("camelot-py is available for table extraction")
        except ImportError:
            logger.warning("camelot-py not available, table extraction will be limited")

        try:
            import fitz  # noqa: F401

            self._fitz_available = True
            logger.info("PyMuPDF (fitz) is available for text extraction")
        except ImportError:
            logger.warning("PyMuPDF not available, text extraction will fail")

        try:
            import pdfplumber  # noqa: F401

            self._pdfplumber_available = True
            logger.info("pdfplumber is available for table extraction")
        except ImportError:
            logger.warning("pdfplumber not available, table extraction fallback limited")

    async def extract_from_storage(
        self, file_content: bytes, file_key: str, max_pages: int | None = None
    ) -> dict[str, Any]:
        """Extract text and tables from PDF file content (from object storage).

        Args:
            file_content: PDF file content as bytes.
            file_key: Storage key/path for logging.
            max_pages: Optional limit on number of pages to process (for testing).

        Returns:
            Dictionary with 'text', 'tables', and 'page_count'.
        """
        return await self._extract_pdf(
            io.BytesIO(file_content), file_identifier=file_key, max_pages=max_pages
        )

    async def extract_from_path(
        self, file_path: str | Path, max_pages: int | None = None
    ) -> dict[str, Any]:
        """Extract text and tables from local PDF file.

        Args:
            file_path: Path to PDF file.
            max_pages: Optional limit on number of pages to process (for testing).

        Returns:
            Dictionary with 'text', 'tables', and 'page_count'.
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        with open(file_path_obj, "rb") as f:
            content = f.read()

        return await self._extract_pdf(
            io.BytesIO(content), file_identifier=str(file_path_obj), max_pages=max_pages
        )

    async def _extract_pdf(
        self,
        pdf_stream: io.BytesIO,
        file_identifier: str | None = None,
        max_pages: int | None = None,
    ) -> dict[str, Any]:
        """Extract text and tables from PDF stream.

        Args:
            pdf_stream: BytesIO stream containing PDF data.
            file_identifier: Identifier for logging (path or key).
            max_pages: Optional limit on number of pages to process (for testing).

        Returns:
            Dictionary with:
            - text: Extracted text content
            - tables: List of extracted tables (as DataFrames or dicts)
            - page_count: Number of pages (actual total, not limited)
            - financial_tables: Tables identified as financial statements
        """
        result = {
            "text": "",
            "tables": [],
            "financial_tables": [],
            "page_count": 0,
        }

        # First, get page count and extract text
        if self._fitz_available:
            text_content, page_count = await self._extract_text_fitz(
                pdf_stream, max_pages=max_pages
            )
            result["text"] = text_content
            result["page_count"] = page_count
        else:
            logger.error("PyMuPDF not available, cannot extract text")
            raise RuntimeError("PyMuPDF required for PDF text extraction")

        # Reset stream for table extraction
        pdf_stream.seek(0)

        # Extract tables using camelot (preferred) or pdfplumber (fallback)
        if self._camelot_available:
            tables = await self._extract_tables_camelot(
                pdf_stream, file_identifier=file_identifier, max_pages=max_pages
            )
            result["tables"] = tables
        elif self._pdfplumber_available:
            tables = await self._extract_tables_pdfplumber(pdf_stream, max_pages=max_pages)
            result["tables"] = tables
        else:
            logger.warning("No table extraction library available")

        # Identify financial tables
        result["financial_tables"] = self._identify_financial_tables(result["tables"])

        file_info = f" ({file_identifier})" if file_identifier else ""
        logger.info(
            f"Extracted PDF{file_info}: {result['page_count']} pages, "
            f"{len(result['tables'])} tables, "
            f"{len(result['financial_tables'])} financial tables"
        )

        return result

    async def _extract_text_fitz(
        self, pdf_stream: io.BytesIO, max_pages: int | None = None
    ) -> tuple[str, int]:
        """Extract text using PyMuPDF (fitz).

        Args:
            pdf_stream: PDF stream.
            max_pages: Optional limit on number of pages to extract.

        Returns:
            Tuple of (text content, page count).
        """
        import fitz

        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        text_content = []
        page_count = len(doc)
        pages_to_extract = min(page_count, max_pages) if max_pages else page_count

        for page_num in range(pages_to_extract):
            page = doc[page_num]
            text_content.append(page.get_text())

        doc.close()

        return "\n\n".join(text_content), page_count

    async def _extract_tables_camelot(
        self,
        pdf_stream: io.BytesIO,
        file_identifier: str | None = None,
        max_pages: int | None = None,
    ) -> list[dict[str, Any]]:
        """Extract tables using camelot-py.

        Args:
            pdf_stream: PDF stream.
            file_identifier: File identifier for temporary file creation.
            max_pages: Optional limit on number of pages to extract.

        Returns:
            List of table dictionaries with 'df' (DataFrame) and metadata.
        """
        import tempfile

        import camelot

        # Camelot requires a file path, so we need to write to temp file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_path = tmp_file.name
            pdf_stream.seek(0)
            tmp_file.write(pdf_stream.read())

        try:
            # Determine pages to extract
            if max_pages:
                pages_str = ",".join(str(i + 1) for i in range(max_pages))
            else:
                pages_str = "all"

            # Extract tables using lattice flavor (best for well-formatted tables)
            try:
                tables = camelot.read_pdf(tmp_path, pages=pages_str, flavor="lattice")
            except Exception as e:
                logger.warning(f"Lattice extraction failed, trying stream: {e}")
                # Try stream flavor as fallback
                tables = camelot.read_pdf(tmp_path, pages=pages_str, flavor="stream")

            # Convert to list of dicts
            table_list = []
            for table in tables:
                # Convert DataFrame to dict for JSON serialization
                df_dict = table.df.to_dict(orient="records")
                table_list.append(
                    {
                        "df": df_dict,
                        "accuracy": table.accuracy,
                        "whitespace": table.whitespace,
                        "page": table.page,
                        "order": table.order,
                    }
                )

            logger.info(f"Extracted {len(table_list)} tables using camelot")
            return table_list

        finally:
            # Clean up temp file
            import os

            try:
                os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {tmp_path}: {e}")

    async def _extract_tables_pdfplumber(
        self, pdf_stream: io.BytesIO, max_pages: int | None = None
    ) -> list[dict[str, Any]]:
        """Extract tables using pdfplumber (fallback).

        Args:
            pdf_stream: PDF stream.
            max_pages: Optional limit on number of pages to extract.

        Returns:
            List of table dictionaries.
        """
        import pdfplumber

        pdf_stream.seek(0)
        table_list = []

        with pdfplumber.open(pdf_stream) as pdf:
            pages_to_process = pdf.pages[:max_pages] if max_pages else pdf.pages
            for page_num, page in enumerate(pages_to_process, start=1):
                tables = page.extract_tables()
                for table_order, table in enumerate(tables, start=1):
                    if table:
                        table_list.append(
                            {
                                "df": table,
                                "page": page_num,
                                "order": table_order,
                                "method": "pdfplumber",
                            }
                        )

        logger.info(f"Extracted {len(table_list)} tables using pdfplumber")
        return table_list

    def _identify_financial_tables(self, tables: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Identify tables that likely contain financial statement data.

        Args:
            tables: List of extracted tables.

        Returns:
            List of financial tables (subset of input tables).
        """
        financial_keywords = [
            "revenue",
            "profit",
            "assets",
            "liabilities",
            "equity",
            "cash flow",
            "income",
            "balance sheet",
            "statement",
            "operations",
            "earnings",
            "expenses",
            "cost of",
        ]

        financial_tables = []

        for table in tables:
            # Check table content for financial keywords
            table_text = ""
            df_data = table.get("df", [])

            # Flatten table content
            if isinstance(df_data, list):
                # Already converted to records
                for row in df_data:
                    if isinstance(row, dict):
                        table_text += " ".join(str(v) for v in row.values()).lower()
            else:
                # DataFrame-like structure
                table_text = str(df_data).lower()

            # Check if table contains financial keywords
            if any(keyword in table_text for keyword in financial_keywords):
                financial_tables.append(table)

        return financial_tables
