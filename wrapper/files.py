from contextlib import contextmanager
from io import BytesIO, StringIO


class InputVirtualFile(StringIO):
    name = "nvs.csv"


class OutputVirtualFile(BytesIO):
    name = "nvs.bin"


@contextmanager
def open_virtual_file(file: InputVirtualFile | OutputVirtualFile, *args, **kwargs):
    file.seek(0)
    try:
        yield file
    finally:
        file.seek(0)
