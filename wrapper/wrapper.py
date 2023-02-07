import logging

from .files import InputVirtualFile, OutputVirtualFile, open_virtual_file
from .input import pre_process_input
from .args import ArgsWithFiles
from .context import managed_monkey_patch

try:
    from . import nvs_partition_gen
except ImportError:
    logging.error("Unable to find nvs_partition_gen.py. Check README.md")
    raise


class Wrapper:
    def __init__(self, input: InputVirtualFile, size: int = 0x3000) -> None:
        processed_input = pre_process_input(input)

        self._input = self._validate_input(processed_input)
        self._size = self._validate_size(size)
        self._output = OutputVirtualFile()

    def _validate_size(self, size):
        return size

    @staticmethod
    def _validate_input(input: InputVirtualFile) -> InputVirtualFile:
        with open_virtual_file(input) as f:
            for line in f:
                if "file" in line:
                    raise NotImplementedError("NVS `file` type is not supported")
        return input

    def generate(self) -> OutputVirtualFile:
        args = ArgsWithFiles(
            input=self._input, output=self._output, size=f"0x{self._size:x}"
        )

        with managed_monkey_patch():
            nvs_partition_gen.generate(args)

        return self._output


def test_wrapper():
    logging.basicConfig(level=logging.INFO)

    NVS_CSV_WITH_FILE_FILENAME = "wrapper/test_stuff/nvs_with_file.csv"
    NVS_BIN_FILENAME = "wrapper/test_stuff/nvs.bin"
    SIZE = 128 * 1024

    from .args import ArgsWithPaths

    args = ArgsWithPaths(
        NVS_CSV_WITH_FILE_FILENAME, NVS_BIN_FILENAME, size=f"0x{SIZE:x}"
    )
    nvs_partition_gen.generate(args)

    with open(NVS_CSV_WITH_FILE_FILENAME, "rt", encoding="utf-8") as csv:
        input = InputVirtualFile(csv.read())
    output = Wrapper(input, size=SIZE).generate()
    with open(NVS_BIN_FILENAME, "rb") as bin:
        assert bin.read() == output.read()
    logging.info("OK")


if __name__ == "__main__":
    test_wrapper()
