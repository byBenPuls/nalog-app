import logging
import datetime
from dataclasses import dataclass

import openpyxl

logger = logging.getLogger(__name__)


@dataclass
class Sale:
    item: str
    document_type: str
    date: datetime.datetime
    quantity: int
    price: int  # in table i saw only int numbers
    # TODO: Use Decimal


class ExelReader:
    def __init__(self, path: str, read_only: bool = False) -> None:
        """
        A simple interface for work with XLSX document
        based by openpyxl
        """
        self.path: str = path
        self.read_only: bool = read_only
        logger.info(
            f"{self.path} opened in {"read only mode" if self.read_only else "write mode"}"
        )
        self.table: openpyxl.Workbook = openpyxl.load_workbook(
            self.path, read_only=self.read_only
        )
        logger.debug(
            f"Openpyxl opened XLSX file; "
            f"available worksheets: {self.table.worksheets}"
        )

    def __enter__(self) -> openpyxl.worksheet.worksheet.Worksheet:
        logger.debug("Reading active sheet")
        return self.table.active

    def __exit__(self, type, value, traceback) -> None:
        logger.info("Closing XLSX connection")
        self.table.close()


class DocumentSalesIterator:
    def __init__(self, document: ExelReader) -> None:
        self.document = document

        self.serialized_rows = []

        self.read_document()

    def get_necessary_data(self, row: tuple):
        if (
            (item := row[2])
            and (document_type := row[9]) == "Продажа"
            and (str_date := row[12])
            and (quantity := row[13])
            and (price := row[15])
        ):
            return Sale(
                item=item,
                document_type=document_type,
                date=datetime.datetime.strptime(str_date, "%Y-%m-%d"),
                quantity=int(quantity),
                price=price,
            )

    def read_document(self):
        with self.document as sheet:
            for i in sheet.iter_rows(values_only=True):
                if data := self.get_necessary_data(i):
                    self.serialized_rows.append(data)

    def __len__(self):
        return len(self.serialized_rows)

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index < len(self.serialized_rows):
            res = self.serialized_rows[self.index]
            self.index += 1
            logging.info(res)
            return res
        else:
            raise StopIteration
