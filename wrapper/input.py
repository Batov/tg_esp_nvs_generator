from .files import InputVirtualFile, open_virtual_file

_INPUT_REPLACEMENTS = {"moeco_cert.pem": "ENV_MOECO_CERT"}


def _get_replacement_env_key(line: str) -> str | None:
    for substring, env_key in _INPUT_REPLACEMENTS.items():
        if substring in line:
            return env_key
    return None


def pre_process_input(input: InputVirtualFile) -> InputVirtualFile:
    result = InputVirtualFile()
    with open_virtual_file(input) as src:
        with open_virtual_file(result) as dst:
            for line in src:
                env_key = _get_replacement_env_key(line)
                if env_key:
                    pass
                else:
                    dst.write(line)
    return result
