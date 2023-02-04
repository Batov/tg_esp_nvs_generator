import builtins
import logging
from dataclasses import dataclass

try:
    from nvs_partition_gen import generate
except ImportError as err:
    logging.error("Unable to find nvs_partition_gen.py. Check README.md")
    raise


@dataclass
class Args:
    input: str = ""
    output: str = ""
    size: str = ""  # nvs_partition_gen expects to find there string with hex number
    version: int = 2
    outdir: str = ""


def generate_nvs(input: bytes, size: int = 0x3000) -> bytes | None:
    input_filename = "input.csv"
    output_filename = "output.bin"

    with open(input_filename, "wb+") as f:
        f.write(input)

    args = Args(input=input_filename, output=output_filename, size=f"0x{size:x}")

    # Redirect print calls to logging
    # lambda concatenates args and removes newlines
    builtins.print = lambda *args: logging.info(" ".join(args).strip())

    try:
        generate(args)
    except Exception as err:
        logging.error(f"nvs_partition_gen.generate error: {err}")

    result = None
    with open(output_filename, "rb") as f:
        result = f.read()

    return result


def test_wrapper():
    logging.basicConfig(level=logging.INFO)
    generate_nvs(b"")


if __name__ == "__main__":
    test_wrapper()
