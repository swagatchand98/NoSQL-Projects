"""Read-only report link comparison; never downloads report binaries."""
import re
from urllib.parse import urljoin,urldefrag
import httpx

def newer_reports(url,known,minimum_year):
    response=httpx.get(url,timeout=20,follow_redirects=True);response.raise_for_status()
    seen=set();rows=[]
    for line in response.text.splitlines():
        years=[int(x) for x in re.findall(r'\b20\d{2}\b',line)]
        if not years or max(years)<minimum_year:continue
        links=re.findall(r'\]\((https?://[^\s)]+)\)|href=["\x27]([^"\x27]+)',line)
        for markdown,html in links:
            target=urldefrag(urljoin(url,markdown or html))[0]
            if target not in seen and target not in known:
                seen.add(target);rows.append({'url':target,'reported_year':max(years),'date_precision':'year from source listing'})
    return rows
