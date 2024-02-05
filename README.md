# aiohttp-client

This module wraps `aiohttp.ClientSession` so that it can be used with APIs such as:

1. HTTP request
    ```py
    import aiohttp_client
    
    async with aiohttp_client.Client() as client:
        r = await client.get("https://httpbin.org/get")  # without "async with"
        print(r.json())  # without "await"
    ```
1. HTTP request (Stream)
    ```py
    import aiohttp_client
    
    async with aiohttp_client.Client() as client:
        async with client.stream("GET", "https://httpbin.org/get") as resp:  # aiohttp conventional API
            print(await resp.json())
    ```
1. WebSocket (**WIP**)
    ```py
    import aiohttp_client
    
    async with aiohttp_client.Client() as client:
        async for ws in client.ws_connect("wss://echo.websoket.events"):  # Reconnection
            print(await ws.recv())
    ```

The purpose of this API is to...

- 1\. and 2\. aim to provide an API similar to `httpx` (`AsyncClient`). When you make HTTP requests in Python, isn't it mostly to get the HTTP (REST) API? In that case, this API makes sense.
    - https://github.com/aio-libs/aiohttp/issues/4346
- 3\. provides a reconnect API similar to `websockets`. Users often want to be able to easily reconnect to WebSocket connections. 
    - https://websockets.readthedocs.io/en/stable/faq/client.html#how-do-i-reconnect-when-the-connection-drops
