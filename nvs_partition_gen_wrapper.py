import logging
from contextlib import contextmanager
from dataclasses import dataclass
from io import BytesIO, StringIO
from typing import Tuple

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
class NvsPartitionGenArgs:
    input: str
    output: str
    size: str = ""
    version: int = 2
    outdir: str = ""


@dataclass
class PatchedNvsPartitionGenArgs(NvsPartitionGenArgs):
    input: InputVirtualFile
    output: OutputVirtualFile


class NvsContentException(Exception):
    pass


class NvsPartitionGenWrapper:
    _INPUT_REPLACEMENTS = [("moeco_cert.pem", "ENV_MOECO_CERT_REPLACE")]

    def __init__(self, input: InputVirtualFile, size: int = 0x3000) -> None:
        self._input = self._process_input(input)
        self._size = self._validate_size(size)
        self._output = OutputVirtualFile()

    def _validate_size(self, size):
        return size

    def _need_do_replacement(self, line: str) -> Tuple[bool, str | None]:
        for substring, env_key in self._INPUT_REPLACEMENTS:
            if substring in line:
                return (True, env_key)
        return (False, None)

    def _check_unsupported_types(self, line: str) -> None:
        if "file" in line:
            raise NvsContentException("NVS `file` type is not supported")

    def _process_input(self, input: InputVirtualFile) -> InputVirtualFile:
        need_replacements = False
        for line in input:
            if not need_replacements:
                need_replacements_in_line, _ = self._need_do_replacement(line)
                if need_replacements_in_line:
                    need_replacements = True
                else:
                    self._check_unsupported_types(line)

        input.seek(0)

        if need_replacements:
            logging.info("Do some replacements")
            new_input = InputVirtualFile()
            for line in input:
                need_replacements_in_line, env_key = self._need_do_replacement(line)
                if need_replacements_in_line:
                    logging.warning(
                        f"TODO: get value from env ({env_key}) and write it here"
                    )
                else:
                    new_input.write(line)
            return new_input

        return input

    @staticmethod
    @contextmanager
    def open_virtual_file(file: InputVirtualFile | OutputVirtualFile, *args, **kwargs):
        try:
            yield file
        finally:
            pass

    def nvs_partition_gen(self) -> OutputVirtualFile:
        args = PatchedNvsPartitionGenArgs(
            input=self._input, output=self._output, size=f"0x{self._size:x}"
        )

        # nvs_partition_gen monkey-patching to handle virtual files instead of real OS files
        origin_os_path_splitext = origin_tool.os.path.splitext
        origin_tool.os.path.splitext = lambda path: origin_os_path_splitext(path.name)
        origin_tool.set_target_filepath = lambda dir, out: (
            dir,
            out,
        )
        origin_tool.open = self.open_virtual_file
        origin_tool.print = lambda *args: logging.info("".join(str(args)))

        self._input.seek(0)
        origin_tool.generate(args)
        self._output.seek(0)

        return self._output


def test_wrapper():
    logging.basicConfig(level=logging.INFO)

    NVS_CSV_WITH_FILE_FILENAME = "nvs_with_file.csv"
    NVS_CSV_FILENAME = "nvs.csv"
    NVS_BIN_FILENAME = "nvs.bin"
    SIZE = 0x3000

    args = NvsPartitionGenArgs(NVS_CSV_FILENAME, NVS_BIN_FILENAME, size=f"0x{SIZE:x}")
    origin_tool.generate(args)

    with open(NVS_CSV_WITH_FILE_FILENAME, "rt", encoding="utf-8") as csv:
        input = InputVirtualFile(csv.read())
    output = NvsPartitionGenWrapper(input, size=SIZE).nvs_partition_gen()
    with open(NVS_BIN_FILENAME, "rb") as bin:
        assert bin.read() == output.read()
    logging.info("OK")


if __name__ == "__main__":
    test_wrapper()
