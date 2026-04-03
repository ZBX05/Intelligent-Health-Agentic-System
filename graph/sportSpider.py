import urllib.request
from lxml import etree
import json
import os
from time import sleep
import time
from random import randint
from typing import Any

def getHTML(url:str,headers:dict,decode:str="utf-8") -> str:
    req=urllib.request.Request(url=url,headers=headers)
    res=urllib.request.urlopen(req)
    html=res.read().decode(decode)
    sleep(15)
    return html

def getContentHTML(html) -> list:
    selector=etree.HTML(html)
    infos=selector.xpath('//body/div[@class="main"]/div[1]/div[@id="mycontent"]/ol/li')
    sub_html=[]
    for info in infos:
        html_list=info.xpath('//dl/dt/a/@href')
        for item in html_list:
            sub_html.append(item)
    return list(set(sub_html))
    
def getText(url:str,headers:dict,decode:str="gbk") -> dict:
    req=urllib.request.Request(url=url,headers=headers)
    res=urllib.request.urlopen(req)
    html=res.read().decode(decode)
    selector=etree.HTML(html)
    title=selector.xpath('//body/div[@class="art_wrap"]/div[@class="art_left"]/h1/text()')
    if(len(title)==0):
        title=""
    else:
        title=title[0]
    summary=selector.xpath('//body/div[@class="art_wrap"]/div[@class="art_left"]/div[@class="art_summary"]/text()')
    if(len(summary)==0):
        summary=""
    else:
        summary=summary[0]
    content_list=selector.xpath('//body/div[@class="art_wrap"]/div[@class="art_left"]/div[@class="art_content"]/p/text()')
    content=""
    for text in content_list:
        content+=text
    sleep(15)
    return {"title":title,"summary":summary,"content":content}

def spiderMain(urls:list,headers:list) -> dict:
    print("="*50,"Start","="*50)
    html_list=[]
    text_dict={"total":0,"contents":[]}
    count_page=1
    for url in urls:
        html=getHTML(url,headers[randint(0,18)])
        content_html_list=getContentHTML(html)
        for item in content_html_list:
            html_list.append(item)
        print(f"Page {count_page} getted.")
        count_page+=1
    sleep(15)
    html_list=list(set(html_list))
    print(html_list)
    print("HTMLs getted.")
    count=1
    block_list=[]
    for url in html_list:
        try:
            content=getText(url,headers[randint(0,18)])
            text_dict["total"]+=1
            text_dict["contents"].append(content)
            print(count,':',text_dict["contents"][-1])
            count+=1
        except Exception:
            print(f"{url} Request blocked, next url.")
            block_list.append(url)
            continue
    print(f"Unblocked total:{count-1}")
    print("Wait for 150 seconds.")
    #等待150秒
    start_wait=time.perf_counter()
    end_wait=start_wait
    while(end_wait-start_wait<=150):
        end_wait=time.perf_counter()
    # sleep(150)
    for url in block_list:
        try:
            content=getText(url,headers[0])
            text_dict["total"]+=1
            text_dict["contents"].append(content)
            print(count,':',text_dict["contents"][-1])
            count+=1
        except Exception:
            print(f"{url} Request blocked, next url.")
            # block_list.append(url)
            continue
    print(f"Total:{count-1}")
    print("Done.")
    return text_dict

if __name__=="__main__":
    urls=["https://so.39.net/search/s?words=%E7%B3%96%E5%B0%BF%E7%97%85%E9%80%82%E5%90%88%E7%9A%84%E8%BF%90%E5%8A%A8&start={}".format(str(i)) for i in range(1,11)]
    # url="https://so.39.net/search/s?words=%E7%B3%96%E5%B0%BF%E7%97%85%E9%80%82%E5%90%88%E7%9A%84%E8%BF%90%E5%8A%A8&start=1"
    headers=[
        {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"},
        {"User-Agent":"Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"},
        {"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"},
        {"User-Agent":"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;"},
        {"User-Agent":"Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)"},
        {"User-Agent":"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)"},
        {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"},
        {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"},
        {"User-Agent":"Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11"},
        {"User-Agent":"Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11"},
        {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"},
        {"User-Agent":"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)"},
        {"User-Agent":"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)"},
        {"User-Agent":"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)"},
        {"User-Agent":"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)"},
        {"User-Agent":"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)"},
        {"User-Agent":"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)"},
        {"User-Agent":"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)"},
        {"User-Agent":"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)"}
    ]

    text_dict=spiderMain(urls,headers)
    with open(os.getcwd()+"/graph/data/spiderData/sport.json","w",encoding="utf-8") as fp:
        json.dump(text_dict,fp,ensure_ascii=False)
    