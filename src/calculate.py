import os
from collections import defaultdict, Counter
from datetime import datetime
from typing import Generator

import pandas
import pymupdf  # type: ignore

from src.check_for_colored import check_for_colored
from src.get_sizes import PageSize, PageSizes, classify_page_size, calculate_a4_equivalent


class AbortionException(Exception):
    pass


class Calculate:
    """
    ######################################################################
    #                            Calculate                                #
    ######################################################################

    Class that processes PDF files in a specified folder and classifies the number of pages and page sizes,
    and saves the results in an Excel file.

    """
    def __init__(self, folder_path: str) -> None:
        self._aborted: bool = False
        self._folder_path: str = folder_path

    def run(self) -> Generator[str, None, None]:
        """
        지정된 폴더 내의 모든 PDF 파일을 처리하여 페이지 수 및 페이지 크기를 분류하고 엑셀 파일로 저장합니다.
        """
        data = []

        filenames = [filename for filename in os.listdir(self._folder_path)
                     if filename.lower().endswith('.pdf')]
        total_files = len(filenames)
        for i, filename in enumerate(filenames, start=1):
            yield f"{i}/{total_files}개 파일 처리 중... ({filename})"

            pdf_path = os.path.join(self._folder_path, filename)
            total_page_sizes, colored_page_sizes, monochrome_page_sizes = self._get_pdf_info(pdf_path)

            page_counts = Counter(total_page_sizes.values())

            data.append({
                'File Name': filename,
                'PDF': sum(page_counts.values()),
                'A4': page_counts.get(PageSize.A4, 0),
                'A3': page_counts.get(PageSize.A3, 0),
                'A2': page_counts.get(PageSize.A2, 0),
                'A1': page_counts.get(PageSize.A1, 0),
                '인쇄 페이지수': calculate_a4_equivalent(total_page_sizes),
                '흑백 페이지수': calculate_a4_equivalent(monochrome_page_sizes),
                '컬러 페이지수': calculate_a4_equivalent(colored_page_sizes),
                '컬러 페이지': ",".join(str(key) for key in colored_page_sizes)
            })

        # Name the output folder
        output_folder = os.path.join(os.getcwd(), "output")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        datetime_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_folder, f'pdf_page_count_{datetime_str}.xlsx')

        # Store the data to an Excel file
        df = pandas.DataFrame(data)
        df.to_excel(output_file, index=False)
        yield f'PDF 정보가 {output_file}에 저장되었습니다.'

    def stop(self) -> None:
        """
        This method is used to stop the execution of a process.
        """
        self._aborted = True

    def _get_pdf_info(self, pdf_path: str) -> tuple[PageSizes, PageSizes, PageSizes]:
        """
        지정된 PDF 파일의 페이지 수와 각 페이지의 크기를 추출하여 반환합니다.
        """
        total_page_sizes: PageSizes = defaultdict()
        colored_page_sizes: PageSizes = defaultdict()
        monochrome_page_sizes: PageSizes = defaultdict()
        with pymupdf.open(pdf_path) as doc:
            print(pdf_path)
            for page_num in range(doc.page_count):
                if self._aborted:
                    self._aborted = False
                    raise AbortionException()
                page = doc.load_page(page_num)
                page_size = classify_page_size(page)
                human_readable_page_num = page_num + 1
                total_page_sizes[human_readable_page_num] = page_size
                if check_for_colored(page):
                    print("Colored page", human_readable_page_num)
                    colored_page_sizes[human_readable_page_num] = page_size
                else:
                    monochrome_page_sizes[human_readable_page_num] = page_size
        return total_page_sizes, colored_page_sizes, monochrome_page_sizes
