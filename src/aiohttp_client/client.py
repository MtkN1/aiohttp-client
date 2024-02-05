import asyncio
import json
from types import SimpleNamespace, TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Iterable,
    List,
    Mapping,
    Optional,
    Type,
    Union,
)

from aiohttp import hdrs, http
from aiohttp.abc import AbstractCookieJar
from aiohttp.client import (
    ClientSession,
    ClientTimeout,
    _CharsetResolver,
    _RequestContextManager,
)
from aiohttp.client_reqrep import ClientRequest, ClientResponse, Fingerprint
from aiohttp.client_ws import ClientWebSocketResponse
from aiohttp.connector import BaseConnector
from aiohttp.helpers import _SENTINEL, BasicAuth, sentinel
from aiohttp.http import HttpVersion
from aiohttp.tracing import TraceConfig
from aiohttp.typedefs import JSONEncoder, LooseCookies, LooseHeaders, StrOrURL

from .client_reqrep import Response

if TYPE_CHECKING:
    from ssl import SSLContext
else:
    SSLContext = None


class Client:
    """First-class interface for making HTTP requests for Humans."""

    def __init__(
        self,
        base_url: Optional[StrOrURL] = None,
        *,
        connector: Optional[BaseConnector] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        cookies: Optional[LooseCookies] = None,
        headers: Optional[LooseHeaders] = None,
        skip_auto_headers: Optional[Iterable[str]] = None,
        auth: Optional[BasicAuth] = None,
        json_serialize: JSONEncoder = json.dumps,
        request_class: Type[ClientRequest] = ClientRequest,
        response_class: Type[ClientResponse] = ClientResponse,
        ws_response_class: Type[ClientWebSocketResponse] = ClientWebSocketResponse,
        version: HttpVersion = http.HttpVersion11,
        cookie_jar: Optional[AbstractCookieJar] = None,
        connector_owner: bool = True,
        raise_for_status: Union[
            bool, Callable[[ClientResponse], Awaitable[None]]
        ] = False,
        read_timeout: Union[float, _SENTINEL] = sentinel,
        conn_timeout: Optional[float] = None,
        timeout: Union[object, ClientTimeout] = sentinel,
        auto_decompress: bool = True,
        trust_env: bool = False,
        requote_redirect_url: bool = True,
        trace_configs: Optional[List[TraceConfig]] = None,
        read_bufsize: int = 2**16,
        max_line_size: int = 8190,
        max_field_size: int = 8190,
        fallback_charset_resolver: _CharsetResolver = lambda r, b: "utf-8",
    ) -> None:
        self._session = ClientSession(
            base_url,
            connector=connector,
            loop=loop,
            cookies=cookies,
            headers=headers,
            skip_auto_headers=skip_auto_headers,
            auth=auth,
            json_serialize=json_serialize,
            request_class=request_class,
            response_class=response_class,
            ws_response_class=ws_response_class,
            version=version,
            cookie_jar=cookie_jar,
            connector_owner=connector_owner,
            raise_for_status=raise_for_status,
            read_timeout=read_timeout,
            conn_timeout=conn_timeout,
            timeout=timeout,
            auto_decompress=auto_decompress,
            trust_env=trust_env,
            requote_redirect_url=requote_redirect_url,
            trace_configs=trace_configs,
            read_bufsize=read_bufsize,
            max_line_size=max_line_size,
            max_field_size=max_field_size,
            fallback_charset_resolver=fallback_charset_resolver,
        )

    @property
    def session(self) -> ClientSession:
        """The aiohttp client session object"""
        return self._session

    def stream(
        self, method: str, url: StrOrURL, **kwargs: Any
    ) -> _RequestContextManager:
        """Perform HTTP request."""
        return self._session.request(method, url, **kwargs)

    def request(self, method: str, url: StrOrURL, **kwargs: Any) -> Awaitable[Response]:
        """Perform HTTP request."""
        return self._request(method, url, **kwargs)

    async def _request(
        self,
        method: str,
        str_or_url: StrOrURL,
        *,
        params: Optional[Mapping[str, str]] = None,
        data: Any = None,
        json: Any = None,
        cookies: Optional[LooseCookies] = None,
        headers: Optional[LooseHeaders] = None,
        skip_auto_headers: Optional[Iterable[str]] = None,
        auth: Optional[BasicAuth] = None,
        allow_redirects: bool = True,
        max_redirects: int = 10,
        compress: Optional[str] = None,
        chunked: Optional[bool] = None,
        expect100: bool = False,
        raise_for_status: Union[
            None, bool, Callable[[ClientResponse], Awaitable[None]]
        ] = None,
        read_until_eof: bool = True,
        proxy: Optional[StrOrURL] = None,
        proxy_auth: Optional[BasicAuth] = None,
        timeout: Union[ClientTimeout, _SENTINEL] = sentinel,
        verify_ssl: Optional[bool] = None,
        fingerprint: Optional[bytes] = None,
        ssl_context: Optional[SSLContext] = None,
        ssl: Union[SSLContext, bool, Fingerprint] = True,
        server_hostname: Optional[str] = None,
        proxy_headers: Optional[LooseHeaders] = None,
        trace_request_ctx: Optional[SimpleNamespace] = None,
        read_bufsize: Optional[int] = None,
        auto_decompress: Optional[bool] = None,
        max_line_size: Optional[int] = None,
        max_field_size: Optional[int] = None,
    ) -> Response:
        async with self._session.request(
            method,
            str_or_url,
            params=params,
            data=data,
            json=json,
            cookies=cookies,
            headers=headers,
            skip_auto_headers=skip_auto_headers,
            auth=auth,
            allow_redirects=allow_redirects,
            max_redirects=max_redirects,
            compress=compress,
            chunked=chunked,
            expect100=expect100,
            raise_for_status=raise_for_status,
            read_until_eof=read_until_eof,
            proxy=proxy,
            proxy_auth=proxy_auth,
            timeout=timeout,
            verify_ssl=verify_ssl,
            fingerprint=fingerprint,
            ssl_context=ssl_context,
            ssl=ssl,
            server_hostname=server_hostname,
            proxy_headers=proxy_headers,
            trace_request_ctx=trace_request_ctx,
            read_bufsize=read_bufsize,
            auto_decompress=auto_decompress,
            max_line_size=max_line_size,
            max_field_size=max_field_size,
        ) as resp:
            body = await resp.read()
            text = await resp.text()

        return Response(
            version=resp.version,
            status=resp.status,
            reason=resp.reason,
            ok=resp.ok,
            method=resp.method,
            url=resp.url,
            real_url=resp.real_url,
            connection=resp.connection,
            content=resp.content,
            cookies=resp.cookies,
            headers=resp.headers,
            raw_headers=resp.raw_headers,
            links=resp.links,
            content_type=resp.content_type,
            charset=resp.charset,
            content_disposition=resp.content_disposition,
            history=resp.history,
            request_info=resp.request_info,
            _body=body,
            text=text,
            _raw_response=resp,
        )

    def ws_connect(
        self,
        url: StrOrURL,
        *,
        method: str = hdrs.METH_GET,
        protocols: Iterable[str] = (),
        timeout: float = 10.0,
        receive_timeout: Optional[float] = None,
        autoclose: bool = True,
        autoping: bool = True,
        heartbeat: Optional[float] = None,
        auth: Optional[BasicAuth] = None,
        origin: Optional[str] = None,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[LooseHeaders] = None,
        proxy: Optional[StrOrURL] = None,
        proxy_auth: Optional[BasicAuth] = None,
        ssl: Union[SSLContext, bool, None, Fingerprint] = True,
        verify_ssl: Optional[bool] = None,
        fingerprint: Optional[bytes] = None,
        ssl_context: Optional[SSLContext] = None,
        proxy_headers: Optional[LooseHeaders] = None,
        compress: int = 0,
        max_msg_size: int = 4 * 1024 * 1024,
    ) -> Any:
        """Initiate websocket connection."""
        return self._ws_connect(
            url,
            method=method,
            protocols=protocols,
            timeout=timeout,
            receive_timeout=receive_timeout,
            autoclose=autoclose,
            autoping=autoping,
            heartbeat=heartbeat,
            auth=auth,
            origin=origin,
            params=params,
            headers=headers,
            proxy=proxy,
            proxy_auth=proxy_auth,
            ssl=ssl,
            verify_ssl=verify_ssl,
            fingerprint=fingerprint,
            ssl_context=ssl_context,
            proxy_headers=proxy_headers,
            compress=compress,
            max_msg_size=max_msg_size,
        )

    async def _ws_connect(
        self,
        url: StrOrURL,
        *,
        method: str = hdrs.METH_GET,
        protocols: Iterable[str] = (),
        timeout: float = 10.0,
        receive_timeout: Optional[float] = None,
        autoclose: bool = True,
        autoping: bool = True,
        heartbeat: Optional[float] = None,
        auth: Optional[BasicAuth] = None,
        origin: Optional[str] = None,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[LooseHeaders] = None,
        proxy: Optional[StrOrURL] = None,
        proxy_auth: Optional[BasicAuth] = None,
        ssl: Optional[Union[SSLContext, bool, Fingerprint]] = True,
        verify_ssl: Optional[bool] = None,
        fingerprint: Optional[bytes] = None,
        ssl_context: Optional[SSLContext] = None,
        proxy_headers: Optional[LooseHeaders] = None,
        compress: int = 0,
        max_msg_size: int = 4 * 1024 * 1024,
    ) -> ClientWebSocketResponse:
        # TODO
        raise NotImplementedError("Client.ws_connect is not implemented")

    def get(
        self, url: StrOrURL, *, allow_redirects: bool = True, **kwargs: Any
    ) -> Awaitable[Response]:
        """Perform HTTP GET request."""
        return self._request(
            hdrs.METH_GET, url, allow_redirects=allow_redirects, **kwargs
        )

    def options(
        self, url: StrOrURL, *, allow_redirects: bool = True, **kwargs: Any
    ) -> Awaitable[Response]:
        """Perform HTTP OPTIONS request."""
        return self._request(
            hdrs.METH_OPTIONS, url, allow_redirects=allow_redirects, **kwargs
        )

    def head(
        self, url: StrOrURL, *, allow_redirects: bool = False, **kwargs: Any
    ) -> Awaitable[Response]:
        """Perform HTTP HEAD request."""
        return self._request(
            hdrs.METH_HEAD, url, allow_redirects=allow_redirects, **kwargs
        )

    def post(
        self, url: StrOrURL, *, data: Any = None, **kwargs: Any
    ) -> Awaitable[Response]:
        """Perform HTTP POST request."""
        return self._request(hdrs.METH_POST, url, data=data, **kwargs)

    def put(
        self, url: StrOrURL, *, data: Any = None, **kwargs: Any
    ) -> Awaitable[Response]:
        """Perform HTTP PUT request."""
        return self._request(hdrs.METH_PUT, url, data=data, **kwargs)

    def patch(
        self, url: StrOrURL, *, data: Any = None, **kwargs: Any
    ) -> Awaitable[Response]:
        """Perform HTTP PATCH request."""
        return self._request(hdrs.METH_PATCH, url, data=data, **kwargs)

    def delete(self, url: StrOrURL, **kwargs: Any) -> Awaitable[Response]:
        """Perform HTTP DELETE request."""
        return self._request(hdrs.METH_DELETE, url, **kwargs)

    def __enter__(self) -> None:
        raise TypeError("Use async with instead")

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        # __exit__ should exist in pair with __enter__ but never executed
        pass  # pragma: no cover

    async def __aenter__(self) -> "Client":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self._session.close()
