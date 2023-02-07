import logging
from contextlib import contextmanager

from .files import open_virtual_file

try:
    from . import nvs_partition_gen
except ImportError:
    logging.error("Unable to find nvs_partition_gen.py. Check README.md")
    raise


@contextmanager
def managed_monkey_patch():
    context = (
        nvs_partition_gen.os.path.splitext,
        nvs_partition_gen.set_target_filepath,
        open,
        print,
    )

    try:
        nvs_partition_gen.os.path.splitext = lambda path: context[0](path.name)
        nvs_partition_gen.set_target_filepath = lambda dir, out: (
            dir,
            out,
        )
        nvs_partition_gen.open = open_virtual_file
        nvs_partition_gen.print = lambda *args: logging.info("".join(str(args)))
        yield None
    finally:
        (
            nvs_partition_gen.os.path.splitext,
            nvs_partition_gen.set_target_filepath,
            nvs_partition_gen.open,
            nvs_partition_gen.print,
        ) = context
