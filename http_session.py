"""
HTTP session management module.
Provides HTTP/1.1 session with connection pooling.
"""

from typing import Optional, Dict
import urllib3


class HTTP11Session:
    """HTTP/1.1 session with connection pooling for efficient requests."""
    
    def __init__(self) -> None:
        """Initialize the HTTP session with connection pool."""
        self.http = urllib3.PoolManager(
            maxsize=100,
            retries=False,
            timeout=urllib3.Timeout(connect=2.0, read=15.0),
            headers={}
        )

    def make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[bytes] = None
    ) -> Optional[urllib3.HTTPResponse]:
        """
        Make an HTTP request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: The request URL.
            headers: Optional request headers.
            body: Optional request body.
            
        Returns:
            HTTPResponse if successful, None if failed.
        """
        try:
            request_headers = {}
            if headers:
                request_headers.update(headers)
                request_headers['Content-Type'] = 'application/json; charset=utf-8'
            
            if method == 'POST':
                if body is None:
                    body = '{"is_retry":true}'.encode('utf-8')
                request_headers['Content-Length'] = str(len(body))
                request_headers['Accept-Encoding'] = 'gzip, deflate, br'
                request_headers['User-Agent'] = 'okhttp/4.12.0'
                request_headers['Connection'] = 'keep-alive'
            
            response = self.http.request(
                method,
                url,
                headers=request_headers,
                body=body,
                preload_content=False
            )
            
            return response
        except urllib3.exceptions.HTTPError:
            return None
        except Exception:
            return None