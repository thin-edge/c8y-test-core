"""Binary assertions"""
import contextlib
import tempfile
from pathlib import Path

from c8y_api.model import Binary

from c8y_test_core.assert_device import AssertDevice


class BinaryReference:
    """Binary references to store both the binary object and the url to it"""

    def __init__(self, binary: Binary, url: str) -> None:
        self.binary = binary
        self.url = url


class Binaries(AssertDevice):
    """Binary assertions"""

    # pylint: disable=too-few-public-methods

    @contextlib.contextmanager
    def new_binary(
        self,
        name: str,
        binary_type: str = "",
        file: str = None,
        contents: str = None,
        **kwargs
    ):
        """Upload a binary and provide it to a context. The binary will be automatically
        deleted one it is done.

        with new_binary("myfile", file="./somefile.txt") as ref:
            print(ref.url)
            print(ref.binary.name)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            if file is None:
                file = Path(tmpdir) / name

                if isinstance(contents, str):
                    Path(file).write_text(contents, encoding="utf8")
                elif isinstance(contents, list):
                    Path(file).write_text("\n".join(contents), encoding="utf8")

            binary = Binary(
                self.context.client,
                type=binary_type,
                name=name,
                file=str(file),
                **kwargs
            ).create()

            binary_url = "/".join(
                [
                    self.context.client.base_url.rstrip("/"),
                    self.context.client.binaries.build_object_path(binary.id).lstrip(
                        "/"
                    ),
                ]
            )
            try:
                # Use custom binary reference as the Binary class does not keep a self reference
                # and even if it did, it is the internal address and not the public domain one
                yield BinaryReference(binary=binary, url=binary_url)
            finally:
                with contextlib.suppress(Exception):
                    binary.delete()
