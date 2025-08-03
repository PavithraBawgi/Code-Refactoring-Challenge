from urllib.parse import urlparse

def validate_url(url):
    try:
        parsed = urlparse(url)
        return all([parsed.scheme in ["http", "https"], parsed.netloc])
    except:
        return False
