from dataclasses import dataclass
from http.cookies import SimpleCookie
from typing import TYPE_CHECKING, Any, Coroutine, Optional, Tuple, Union

from aiohttp import hdrs
from aiohttp.client_exceptions import ContentTypeError
from aiohttp.client_reqrep import (
    ClientResponse,
    ContentDisposition,
    RequestInfo,
    _is_expected_content_type,
)
from aiohttp.http import HttpVersion
from aiohttp.streams import StreamReader
from aiohttp.typedefs import DEFAULT_JSON_DECODER, JSONDecoder, RawHeaders
from multidict import CIMultiDictProxy, MultiDictProxy
from yarl import URL

if TYPE_CHECKING:
    from aiohttp.connector import Connection


class Request:
    pass


@dataclass
class Response:
    version: HttpVersion
    status: int
    reason: str
    ok: bool
    method: str
    url: URL
    real_url: URL
    connection: Optional["Connection"]
    content: StreamReader
    cookies: SimpleCookie
    headers: CIMultiDictProxy
    raw_headers: RawHeaders
    links: "MultiDictProxy[MultiDictProxy[Union[str, URL]]]"
    content_type: str
    charset: Optional[str]
    content_disposition: Optional[ContentDisposition]
    history: Tuple["ClientResponse", ...]
    request_info: RequestInfo

    _body: bytes
    text: str

    _raw_response: ClientResponse

    def close(self) -> None:
        return self._raw_response.close()

    def read(self) -> Coroutine[Any, Any, bytes]:
        return self._raw_response.read()

    def release(self) -> Any:
        return self._raw_response.release()

    def raise_for_status(self) -> None:
        return self._raw_response.raise_for_status()

    def json(
        self,
        *,
        encoding: Optional[str] = None,
        loads: JSONDecoder = DEFAULT_JSON_DECODER,
        content_type: Optional[str] = "application/json",
    ) -> Any:
        """Read and decodes JSON response."""
        if content_type:
            ctype = self.headers.get(hdrs.CONTENT_TYPE, "").lower()
            if not _is_expected_content_type(ctype, content_type):
                raise ContentTypeError(
                    self.request_info,
                    self.history,
                    message=(
                        "Attempt to decode JSON with " "unexpected mimetype: %s" % ctype
                    ),
                    headers=self.headers,
                )

        stripped = self._body.strip()  # type: ignore[union-attr]
        if not stripped:
            return None

        if encoding is None:
            encoding = self.get_encoding()

        return loads(stripped.decode(encoding))

    def get_encoding(self) -> str:
        return self._raw_response.get_encoding()
