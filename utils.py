import sys

from PIL import Image

class Color:
    RED = "\033[91m"
    GREEN = "\033[92m"
    ORANGE = "\033[93m"
    END = "\033[0m"


def convert_to_degrees(value):
    """
    Helper function to convert GPS coordinates stored in the EXIF to degrees in float format
    :param value:
    :type value: exifread.utils.Ratio
    :rtype float
    """
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)
    return d + (m / 60.0) + (s / 3600.0)


def print_result(status: int, to_print: str):
    """
    Print result and change color in function of status code
    :param status: 0 if it's ok, 1 if not, 2 if color already defined
    :param to_print:
    :return:
    """
    if status == 1:
        print(Color.RED + to_print, Color.END)
        sys.exit(1)
    if status == 2:
        print(to_print)
    else:
        if type(to_print) == dict:
            for item in to_print.keys():
                print(
                    Color.GREEN + f'[+]'
                    f'{item}: {to_print[item]}',
                    Color.END
                )
        else:
            print(Color.GREEN + to_print, Color.END)


def add_primary_info(image: Image):
    new_dict = {
        'Filename': image.filename,
        'Format': image.format,
        'Mode': image.mode,
        'Width': image.width,
        'Height': image.height,
        'Palette': image.palette,
    }

    return new_dict
