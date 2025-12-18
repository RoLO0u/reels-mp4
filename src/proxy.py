from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class ProxyConfig:
    test_url: str
    proxy: str
    proxy_auth: str

    @property
    def proxy_url(self) -> str:
        """Proxy URL suitable for `requests`, including credentials if provided.

        Mirrors the logic from `scripts/test_proxy_instaloader.py`:
        - If `PROXY` has no scheme, default to http://
        - If `PROXY_AUTH` is set and proxy_url has no '@', inject user:pass
        - If auth is malformed, leave URL unchanged
        """

        proxy_url = (self.proxy or "").strip()
        if not proxy_url:
            return ""

        if "://" not in proxy_url:
            proxy_url = f"http://{proxy_url}"

        if self.proxy_auth and "@" not in proxy_url:
            auth = self.proxy_auth.strip()
            if ":" in auth:
                user, pwd = auth.split(":", 1)
                if user and pwd:
                    proxy_url = proxy_url.replace("://", f"://{user}:{pwd}@", 1)

        # Basic sanity: urlparse should see a host; if not, keep raw string.
        parsed = urlparse(proxy_url)
        if not parsed.hostname:
            return proxy_url
        return proxy_url

    @property
    def requests_proxies(self) -> dict[str, str]:
        url = self.proxy_url
        if not url:
            return {}
        return {"http": url, "https": url}


def load_proxy_config_from_env() -> ProxyConfig:
    return ProxyConfig(
        test_url=os.getenv("TEST_URL") or "https://ipv4.icanhazip.com",
        proxy=os.getenv("PROXY") or "",
        proxy_auth=os.getenv("PROXY_AUTH") or "",
    )
