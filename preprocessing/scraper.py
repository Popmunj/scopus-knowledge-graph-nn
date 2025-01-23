import requests
from bs4 import BeautifulSoup
from bs4 import Tag
import json



def get_citation(title):
    res = requests.get("https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={}&btnG=".format(title),
                   headers={
                       "User-Agent": "Mozilla/5.0 (Linux; U; Android 10; en-US; RMX1901 Build/QKQ1.190918.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.108 UCBrowser/13.4.0.1306 Mobile Safari/537.36"
                   })
    
    soup = BeautifulSoup(res.text, "lxml")
    
    col = soup.find_all(id="gs_res_ccl_mid")
    if len(col) == 0:
        return None
    
    # check name
    for p in col:
        name = p.find(attrs={"class": "gs_rt"}).find("a")
        if name.string:
            tbc = name.string
        else:
            r = []
            for e in name.contents:
                if isinstance(e, str):
                    r.append(e)
                elif isinstance(e, Tag):
                    r.append(e.string)
            tbc = "".join(r)
        
        if len(title) > 160:
            title = title[:160]
            tbc = tbc[:160]
        
        if tbc == title: 
            return int(soup.find_all(id="gs_res_ccl_mid")[0].find(attrs={"class":"gs_fl gs_flb"}).find_all("a")[2].string.replace("Cited by ", ""))
