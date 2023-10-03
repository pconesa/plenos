from urllib.parse import parse_qs, urlparse

def extractYoutubeId(url):
    if "youtu.be" in url:
        # https://youtu.be/qbgSP1SLimg?t=1446
        o = urlparse(url)
        return o.path
    else:
        return extractGetParamFromURL(url, 'v')

def extractYoutubeStart(url):
    return extractGetParamFromURL(url, 't', default="0")

def extractGetParamFromURL(url, paramName, default=""):
    return parse_qs(urlparse(url).query).get(paramName,[default])[0]
