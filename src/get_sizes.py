from collections import defaultdict, Counter
from enum import IntEnum

import pymupdf  # type: ignore


class PageSize(IntEnum):
    """
    This code defines a class called `PageSize` which is an enumeration of different page sizes. The page sizes are defined as integer values using the `IntEnum` class.
    """
    A4 = 0
    A3 = 1
    A2 = 2
    A1 = 3


PageSizes = defaultdict[int, PageSize]


def classify_page_size(page: pymupdf.Page) -> PageSize:
    """
    페이지의 크기를 면적 기준으로 정렬
    """
    width, height = page.mediabox_size
    area = width * height * (0.352778 ** 2)  # pt를 mm로 변환

    if area < 80000:
        return PageSize.A4
    elif area < 150000:
        return PageSize.A3
    elif area < 300000:
        return PageSize.A2
    else:
        return PageSize.A1


def calculate_a4_equivalent(page_sizes: PageSizes) -> int:
    """
    각 페이지 크기에 따라 A4 페이지로 환산한 값을 계산합니다.
    """
    page_counts = Counter(page_sizes.values())
    a4_equivalent = (page_counts.get(PageSize.A4, 0) +
                     page_counts.get(PageSize.A3, 0) * 2 +
                     page_counts.get(PageSize.A2, 0) * 4 +
                     page_counts.get(PageSize.A1, 0) * 8)
    return a4_equivalent
