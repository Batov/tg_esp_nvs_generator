from io import StringIO, BytesIO
import logging
import contextlib
from dataclasses import dataclass
import os

try:
    import nvs_partition_gen
except ImportError:
    logging.error("Unable to find nvs_partition_gen.py. Check README.md")
    raise


class InputFile(StringIO):
    name = "nvs.csv"


class OutputFile(BytesIO):
    name = "nvs.bin"


@dataclass
class Args:
    input: InputFile
    output: OutputFile
    size: str = ""  # nvs_partition_gen expects to find there string with hex number
    version: int = 2
    outdir: str = ""


@contextlib.contextmanager
def open_virtual_file(file: InputFile | OutputFile, *args, **kwargs):
    try:
        yield file
    finally:
        pass


def generate_nvs(input: InputFile, size: int = 0x3000) -> OutputFile:
    output = OutputFile()

    args = Args(input=input, output=output, size=f"0x{size:x}")

    # nvs_partition_gen monkey-patching to handle virtual files instead of real OS files
    origin_os_path_splitext = nvs_partition_gen.os.path.splitext
    nvs_partition_gen.os.path.splitext = lambda path: origin_os_path_splitext(path.name)
    nvs_partition_gen.set_target_filepath = lambda outdit, output: (outdit, output)
    nvs_partition_gen.open = open_virtual_file
    nvs_partition_gen.print = lambda *args: logging.info("".join(str(args)))

    try:
        nvs_partition_gen.generate(args)
    except Exception as err:
        logging.error(f"nvs_partition_gen.generate error: {err}")
        raise
    else:
        output.seek(0)

    return output


def test_wrapper():
    logging.basicConfig(level=logging.INFO)

    with open("nvs.csv", "rt") as f:
        input = InputFile(f.read())
        output = generate_nvs(input)
        logging.info(f"Output bin file length: {len(output.read())} bytes")


if __name__ == "__main__":
    test_wrapper()
