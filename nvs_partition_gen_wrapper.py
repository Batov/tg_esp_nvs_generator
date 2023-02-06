import logging
import os
from contextlib import contextmanager
from dataclasses import dataclass
from io import BytesIO, StringIO

try:
    import nvs_partition_gen as origin_tool
except ImportError:
    logging.error("Unable to find nvs_partition_gen.py. Check README.md")
    raise


class InputVirtualFile(StringIO):
    name = "nvs.csv"


class OutputVirtualFile(BytesIO):
    name = "nvs.bin"


@dataclass
class Args:
    input: InputVirtualFile
    output: OutputVirtualFile
    size: str = ""  # nvs_partition_gen expects to find there string with hex number
    version: int = 2
    outdir: str = ""


class NvsPartitionGenException(Exception):
    pass


class NvsPartitionGenWrapper:
    def __init__(self, input: InputVirtualFile, size: int = 0x3000) -> None:
        self._input = self._is_valid_input(input)
        self._size = self._is_valid_size(size)
        self._output = OutputVirtualFile()

    def _is_valid_input(self, input):
        for line in input.readlines():
            if "file" in line:
                raise NvsPartitionGenException("NVS `file` type is not supported")
        return input

    def _is_valid_size(self, size):
        return size

    @staticmethod
    @contextmanager
    def open_virtual_file(file: InputVirtualFile | OutputVirtualFile, *args, **kwargs):
        try:
            yield file
        finally:
            pass

    def nvs_partition_gen(self) -> OutputVirtualFile:
        args = Args(input=self._input, output=self._output, size=f"0x{self._size:x}")

        origin_os_path_splitext = origin_tool.os.path.splitext

        # nvs_partition_gen monkey-patching to handle virtual files instead of real OS files
        origin_tool.os.path.splitext = lambda path: origin_os_path_splitext(path.name)
        origin_tool.set_target_filepath = lambda dir, out: (
            dir,
            out,
        )
        origin_tool.open = self.open_virtual_file
        origin_tool.print = lambda *args: logging.info("".join(str(args)))

        origin_tool.generate(args)

        self._output.seek(0)
        return self._output


def test_wrapper():
    logging.basicConfig(level=logging.INFO)

    with open("nvs.csv", "rt") as f:
        input = InputVirtualFile(f.read())
        wrapper = NvsPartitionGenWrapper(input)
        output = wrapper.nvs_partition_gen()
        logging.info(f"Output bin file length: {len(output.read())} bytes")


if __name__ == "__main__":
    test_wrapper()
