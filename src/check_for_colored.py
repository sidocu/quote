import pymupdf  # type: ignore
import numpy as np


def check_for_colored(page: pymupdf.Page) -> bool:
    """
    Checks if a given page in a PDF document contains colored content.

    Parameters:
        page (pymupdf.Page): The page to be checked for colored content.

    Returns:
        bool: True if the page contains colored content, False otherwise.

    This function determines whether a page in a PDF document contains colored content by analyzing the pixel values of the page's pixmap. The pixmap is obtained using the `get_pixmap()` method of the `Page` class from the `pymupdf` library.

    First, the function checks if the pixmap is a single channel image (monochrome), in which case it returns False since there is no colored content in a monochrome image.

    If the pixmap has an alpha channel, it is converted to RGB using the `Pixmap` class from the `pymupdf` library.

    Next, the function converts the pixmap to a NumPy array for pixel analysis. The array has a shape of (height, width, channels), where channels represent the color channels (e.g., RGB or RGBA).

    A tolerance value of 10 is set to define the maximum color difference allowed between channels for a pixel to be considered colored.

    The function calculates the absolute differences between the red (R) and green (G) channels, and between the green (G) and blue (B) channels, using NumPy array operations.

    Pixels where either the difference between the red and green channels or the difference between the green and blue channels exceeds the tolerance are considered to have significant color difference.

    The function then obtains the coordinates of the colored pixels by finding the indices of True values in the array of significant color differences using NumPy's `where()` function.

    Finally, the function returns True if there are any colored pixels in the page, which is determined by checking if the length of the colored coordinates array is greater than 0. Otherwise, it returns False.

    Note: This function requires the `pymupdf` and `numpy` libraries to be installed in the Python environment.
    """
    pixmap = page.get_pixmap()
    if pixmap.n < 3:
        # Single channel image, already monochrome
        return False
    elif pixmap.n == 4:
        # Convert to RGB if the image has an alpha channel
        pixmap = pymupdf.Pixmap(pymupdf.csRGB, pixmap)

    # Convert to NumPy array for pixel analysis
    img = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
        pixmap.height, pixmap.width, pixmap.n)
    img = img.astype(np.int16)

    tolerance = 10  # Color difference tolerance

    # Calculate absolute differences between the channels
    diff_rg = np.abs(img[:, :, 0] - img[:, :, 1])
    diff_gb = np.abs(img[:, :, 1] - img[:, :, 2])

    # Identify pixels where the difference exceeds the tolerance
    significant_diff = (diff_rg > tolerance) | (diff_gb > tolerance)

    # Get the coordinates of the colored pixels
    colored_coords = np.column_stack(np.where(significant_diff))

    return len(colored_coords) > 0
