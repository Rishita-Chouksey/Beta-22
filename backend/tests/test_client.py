"""Synchronous test facade over httpx ASGITransport (works with Python 3.14)."""
import asyncio
import os

import httpx
import pytest

class ApiTestClient:
    def __init__(self, app, base_url="http://testserver"):
        self.app = app
        self.base_url = base_url
        self.cookies = httpx.Cookies()

    def request(self, method, url, **kwargs):
        if os.getenv("YOJNASARTHI_SKIP_ASGI_TESTS") == "1":
            pytest.skip("ASGI HTTP tests skipped because this runner blocks loopback socketpairs.")
        async def send():
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=self.app),
                base_url=self.base_url,
                cookies=self.cookies,
            ) as client:
                response = await client.request(method, url, **kwargs)
                self.cookies.update(client.cookies)
                return response
        return asyncio.run(send())

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)
