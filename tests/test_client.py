import pytest
import pytest_asyncio
from aiohttp import ClientResponse, ClientSession, hdrs
from aiohttp_client import Client, Response
from pytest_httpbin.serve import Server


@pytest.mark.asyncio
async def test_client_instance():
    async with Client() as client:
        assert isinstance(client.session, ClientSession)


@pytest_asyncio.fixture
async def client_instance():
    async with Client() as client:
        yield client


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("http_method",),
    [
        (hdrs.METH_GET,),
        # (hdrs.METH_OPTIONS,),
        # (hdrs.METH_HEAD,),
        (hdrs.METH_POST,),
        (hdrs.METH_PUT,),
        (hdrs.METH_PATCH,),
        (hdrs.METH_DELETE,),
    ],
)
async def test_request(httpbin: Server, client_instance: Client, http_method: str):
    url = f"{httpbin.url}/{http_method.lower()}"

    resp = await client_instance.request(http_method, url)

    assert isinstance(resp, Response)
    data = resp.json()

    assert data["url"] == url


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("http_method",),
    [
        (hdrs.METH_GET,),
        # (hdrs.METH_OPTIONS,),
        # (hdrs.METH_HEAD,),
        (hdrs.METH_POST,),
        (hdrs.METH_PUT,),
        (hdrs.METH_PATCH,),
        (hdrs.METH_DELETE,),
    ],
)
async def test_request_method(
    httpbin: Server, client_instance: Client, http_method: str
):
    url = f"{httpbin.url}/{http_method.lower()}"

    resp = await getattr(client_instance, http_method.lower())(url)

    assert isinstance(resp, Response)
    data = resp.json()

    assert data["url"] == url


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("http_method",),
    [
        (hdrs.METH_GET,),
        # (hdrs.METH_OPTIONS,),
        # (hdrs.METH_HEAD,),
        (hdrs.METH_POST,),
        (hdrs.METH_PUT,),
        (hdrs.METH_PATCH,),
        (hdrs.METH_DELETE,),
    ],
)
async def test_request_stream(
    httpbin: Server, client_instance: Client, http_method: str
):
    url = f"{httpbin.url}/{http_method.lower()}"

    async with client_instance.stream(http_method, url) as resp:
        assert isinstance(resp, ClientResponse)
        data = await resp.json()

    assert data["url"] == url
