"""
FraudLens AI - URL & SSRF Security Utilities
Performs domain extraction, URL normalization, and robust SSRF defense against private network targets.
"""

import ipaddress
import socket
import urllib.parse
from app.exceptions import SSRFSecurityError, ValidationError

BLOCKED_HOSTNAMES = {
    "localhost", "127.0.0.1", "0.0.0.0", "::1", "metadata.google.internal",
    "instance-data", "169.254.169.254"
}

def normalize_url(raw_url: str) -> str:
    """Normalizes a URL by trimming whitespace, ensuring scheme, and lowercasing hostname."""
    if not raw_url or not isinstance(raw_url, str):
        raise ValidationError("URL string is required")
        
    url = raw_url.strip()
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    parsed = urllib.parse.urlparse(url)
    if not parsed.netloc:
        raise ValidationError(f"Invalid URL structure: {raw_url}")

    hostname = parsed.hostname or ""
    path = parsed.path or "/"
    
    # Clean normalized URL representation
    normalized = f"{parsed.scheme}://{hostname.lower()}{path}"
    if parsed.query:
        normalized += f"?{parsed.query}"
    return normalized

def extract_domain(raw_url: str) -> str:
    """Extracts and strips leading 'www.' and ports from a URL."""
    if not raw_url:
        return ""
    url = raw_url.strip()
    if not url.startswith(("http://", "https://", "ftp://")):
        url = f"http://{url}"
    try:
        parsed = urllib.parse.urlparse(url)
        hostname = (parsed.hostname or "").lower()
        if hostname.startswith("www."):
            hostname = hostname[4:]
        return hostname
    except Exception:
        return ""

def validate_ssrf_safety(raw_url: str) -> bool:
    """
    Validates that a URL does not target loopback, private RFC1918, link-local,
    or internal cloud metadata IP addresses.
    """
    if not raw_url:
        raise ValidationError("URL cannot be empty")
        
    url = raw_url.strip().lower()
    if url.startswith(("file://", "ftp://", "gopher://", "ldap://", "data:")):
        raise SSRFSecurityError("Unsupported or hazardous protocol scheme")

    try:
        parsed = urllib.parse.urlparse(url if "://" in url else f"https://{url}")
        hostname = parsed.hostname
        if not hostname:
            raise ValidationError("Could not resolve URL hostname")

        if hostname in BLOCKED_HOSTNAMES or hostname.endswith(".localhost"):
            raise SSRFSecurityError(f"Access to restricted hostname '{hostname}' is blocked")

        # Resolve IP to detect loopback or private ranges
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for item in addr_info:
                ip_str = item[4][0]
                ip = ipaddress.ip_address(ip_str)
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                    raise SSRFSecurityError(f"Target hostname resolves to a prohibited internal IP address: {ip_str}")
        except socket.gaierror:
            # If domain cannot be resolved via DNS, it's not a private IP access, but may not be reachable
            pass

        return True
    except SSRFSecurityError:
        raise
    except Exception as e:
        raise ValidationError(f"Invalid URL structure: {str(e)}")
