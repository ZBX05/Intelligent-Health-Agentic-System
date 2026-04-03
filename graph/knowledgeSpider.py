import urllib.request
from lxml import etree
import json
import os
from time import sleep
import time
from random import randint

def get_html(url:str,headers:dict,decode:str='utf-8'):
    req=urllib.request.Request(url=url,headers=headers)
    res=urllib.request.urlopen(req)
    html=res.read().decode(decode)
    sleep(15)
    return html

def get_content_html(html:str) -> list:
    selector=etree.HTML(html)
    infos=selector.xpath('//body//div[@class="disease_box"]//div[@class="result_content"]/div[@class="result_item"]')
    sub_html=[]
    for info in infos:
        html_list=info.xpath('//p[@class="result_item_top_l"]/a/@href')
        item_list=info.xpath('//p[@class="result_item_top_l"]/a/@title')
        for item_1,item_2 in zip(html_list,item_list):
            sub_html.append((item_1,item_2))
    return sub_html

def get_disease_text(url:str,headers:dict,decode:str="utf-8") -> dict:
    req=urllib.request.Request(url=url,headers=headers)
    res=urllib.request.urlopen(req)
    html=res.read().decode(decode)
    selector=etree.HTML(html)
    disease_box=selector.xpath('//body/div[@class="container"]/div[@class="list_left"]/div[@class="disease_box"]/ul[@class="information_ul"]')[0]
    drugs=selector.xpath('//body//div[@class="disease_box"]/ul[@class="information_ul information_ul_bottom"]/li[1]/span')[0]
    symptoms=disease_box.xpath("//i[text()='典型症状：']/../span/a")
    anatomys=disease_box.xpath("//i[text()='发病部位：']/../span/a")
    departments=disease_box.xpath("//i[text()='挂号科室：']/../span/a")
    infectivity=disease_box.xpath("//i[text()='传染性：']/../span/text()")
    period=disease_box.xpath("//i[text()='治疗周期：']/../span/text()")
    tests=disease_box.xpath("//i[text()='临床检查：']/../span/a")
    disease=selector.xpath('//body/div[@class="container"]/div[@class="disease_box"]/div/h1/text()')[0]
    symptom=[]
    test=[]
    drug=[]
    anatomy=[]
    department=[]
    for d in drugs:
        drug.extend(d.xpath('text()'))
    for s in symptoms:
        symptom.extend(s.xpath('text()'))
    for a in anatomys:
        anatomy.extend(a.xpath('text()'))
    for d in departments:
        department.extend(d.xpath('text()'))
    for t in tests:
        test.extend(t.xpath('text()'))
    
    sleep(15)
    return {"disease":disease,"drug":drug,"anatomy":anatomy,"symptom":symptom,"department":department,"test":test,
            "infectivity":infectivity,"period":period}

def get_symptom_text(url:str,headers:dict,decode:str="utf-8") -> dict:
    req=urllib.request.Request(url=url,headers=headers)
    res=urllib.request.urlopen(req)
    html=res.read().decode(decode)
    selector=etree.HTML(html)
    item=selector.xpath('//body//div[@class="item"]')[0]
    infos=item.xpath('//td[@class="name"]/..')
    symptom_disease=[]
    department_disease=[]
    disease=[]
    disease_html=[]
    department=[]
    symptom=selector.xpath('//body//header//h1/text()')[0]
    for info in infos:
        d=[d_ for d_ in info.xpath('//td[@class="name"]/a/@title')]
        disease.extend(d)
    disease=list(set(disease))
    symptom_disease=[[symptom,dise] for dise in disease]
    # for info in infos:
    #     d=[d_ for d_ in info.xpath('//td[@class="name"]/a/@title')]
    #     d_html=info.xpath('//td[@class="name"]/a/@href')[0]
    #     s=[s_ for s_ in info.xpath('//td[@class="name"]/../td[2]/a/@title')]
    #     de=[de_ for de_ in info.xpath('//td[@class="name"]/../td[3]/a/@title')]
    #     disease.extend(d)
    #     symptom.extend(s)
    #     department.extend(de)    
    #     disease_html.append(d_html)
    # symptom_disease.extend([[symp,sub_d] for sub_d in d for symp in s])
    # department_disease.extend([[dep,sub_d] for sub_d in d for dep in de])
    sleep(15)
    # return {"content":{"disease":list(set(disease)),"symptom":list(set(symptom)),"department":list(set(department)),
    #                    "symptom_disease":symptom_disease,"department_disease":department_disease},"disease_html":disease_html}
    return {"content":{"disease":list(set(disease)),"symptom":symptom,"symptom_disease":symptom_disease},"disease_html":disease_html}

def get_test_text(url:tuple,headers:dict,decode:str="utf-8") -> dict:
    req=urllib.request.Request(url=url[0],headers=headers)
    res=urllib.request.urlopen(req)
    html=res.read().decode(decode)
    selector=etree.HTML(html)
    test=url[1]
    diseases=selector.xpath('//body//div[@id="refdisease"]//div[@class="listBox"]//ul//a')
    disease=[]
    test_disease=[]
    disease_html=[]
    for a in diseases:
        disease.extend(a.xpath('text()'))
        disease_html.extend(a.xpath('@href'))
    test_disease.extend([[test,d] for d in disease])
    sleep(15)
    return {"content":{"disease":disease,"test":test,"test_disease":test_disease},"disease_html":disease_html}

def get_operation_text(url:tuple,headers:dict,decode:str="utf-8") -> dict:
    req=urllib.request.Request(url=url[0],headers=headers)
    res=urllib.request.urlopen(req)
    html=res.read().decode(decode)
    selector=etree.HTML(html)
    operation=url[1]
    diseases=selector.xpath('//body//div[@id="refDisease"]//div[@class="listBox"]//ul//a')
    disease=[]
    operation_disease=[]
    disease_html=[]
    for a in diseases:
        disease.extend(a.xpath('text()'))
        disease_html.extend(a.xpath('@href'))
        operation_disease.extend([[operation,d] for d in disease])
    
    sleep(15)
    return {"content":{"disease":disease,"operation":operation,"operation_disease":operation_disease},"disease_html":disease_html}

def get_symptom_data(urls:list,headers:list) -> dict:
    '''爬取症状页面的数据'''
    print("Fetching symptom data...")
    html_list=[]
    html_list_=[]
    text_dict={"total":0,"contents":[],"disease_html":[]}
    count_page=1
    for url in urls:
        html=get_html(url,headers[randint(0,18)])
        content_html_list=get_content_html(html)
        for item in content_html_list:
            html_list.append(item)
        print(f"Page {count_page} getted.")
        count_page+=1
    # html_list=list(set(html_list))
    for url_tuple in html_list:
        html_list_.append(url_tuple[0])
    html_list=list(set(html_list_))
    print(html_list)
    print("Symptom HTMLs getted.")
    sleep(15)
    count=1
    block_list=[]
    for url in html_list:
        try:
            content=get_symptom_text(url,headers[randint(0,18)])
            text_dict["total"]+=1
            text_dict["contents"].append(content["content"])
            text_dict["disease_html"].extend(text_dict["disease_html"])
            print(count,':',text_dict["contents"][-1])
            count+=1
        except Exception as e:
            print(e)
            print(f"{url} Request blocked, next url.")
            block_list.append(url)
            continue
    print(f"Unblocked total:{count-1}")
    print("Wait for 5 seconds.")
    #等待15秒
    sleep(15)
    # sleep(150)
    for url in block_list:
        try:
            content=get_symptom_text(url,headers[0])
            text_dict["total"]+=1
            text_dict["contents"].append(content["content"])
            text_dict["disease_html"].extend(text_dict["disease_html"])
            print(count,':',text_dict["contents"][-1])
            count+=1
        except Exception as e:
            print(f"{url} Request blocked, next url.")
            continue
    print(f"Symptom total:{count-1}")
    print("Done symptom.")
    return text_dict

def get_test_data(urls:list,headers:list) -> dict:
    '''爬取检查页面的数据'''
    print("Fetching test data...")
    html_list=[]
    html_list_final=[]
    html_record=[]
    text_dict={"total":0,"contents":[],"disease_html":[]}
    count_page=1
    for url in urls:
        html=get_html(url,headers[randint(0,18)])
        content_html_list=get_content_html(html)
        for item in content_html_list:
            html_list.append(item)
        print(f"Page {count_page} getted.")
        count_page+=1
    # html_list=list(set(html_list))
    for url_tuple in html_list:
        if(url_tuple[0] not in html_record):
            html_list_final.append(url_tuple)
            html_record.append(url_tuple[0])
    html_list=html_list_final
    print(html_list)
    print("Test HTMLs getted.")
    sleep(15)
    count=1
    block_list=[]
    for url in html_list:
        try:
            content=get_test_text(url,headers[randint(0,18)])
            text_dict["total"]+=1
            text_dict["contents"].append(content["content"])
            text_dict["disease_html"].extend(text_dict["disease_html"])
            print(count,':',text_dict["contents"][-1])
            count+=1
        except Exception as e:
            print(f"{url} Request blocked, next url.")
            block_list.append(url)
            continue
    print(f"Unblocked total:{count-1}")
    print("Wait for 5 seconds.")
    #等待15秒
    sleep(15)
    # sleep(150)
    for url in block_list:
        try:
            content=get_test_text(url,headers[0])
            text_dict["total"]+=1
            text_dict["contents"].append(content["content"])
            text_dict["disease_html"].extend(text_dict["disease_html"])
            print(count,':',text_dict["contents"][-1])
            count+=1
        except Exception as e:
            print(f"{url} Request blocked, next url.")
            continue
    print(f"Test total:{count-1}")
    print("Done test.")
    return text_dict

def get_disease_data(urls:list,outer_urls:list,headers:list) -> dict:
    '''爬取疾病页面的数据'''
    print("Fetching disease data...")
    html_list_total=[]
    html_list=[]
    text_dict={"total":0,"contents":[]}
    count_page=1
    for url in urls:
        html=get_html(url,headers[randint(0,18)])
        content_html_list=get_content_html(html)
        for item in content_html_list:
            html_list.append(item)
        print(f"Page {count_page} getted.")
        count_page+=1
    # html_list=list(set(html_list))
    for url in html_list:
        html_list_total.append(url[0])
    html_list_total.extend(outer_urls)
    html_list=list(set(html_list_total))
    print(html_list)
    print("Disease HTMLs getted.")
    sleep(15)
    count=1
    block_list=[]
    for url in html_list:
        try:
            content=get_disease_text(url,headers[randint(0,18)])
            text_dict["total"]+=1
            text_dict["contents"].append(content)
            print(count,':',text_dict["contents"][-1])
            count+=1
        except Exception as e:
            print(f"{url} Request blocked, next url.")
            block_list.append(url)
            continue
    print(f"Unblocked total:{count-1}")
    print("Wait for 5 seconds.")
    #等待15秒
    sleep(15)
    # sleep(150)
    for url in block_list:
        try:
            content=get_disease_text(url,headers[0])
            text_dict["total"]+=1
            text_dict["contents"].append(content["content"])
            print(count,':',text_dict["contents"][-1])
            count+=1
        except Exception as e:
            print(f"{url} Request blocked, next url.")
            continue
    print(f"Disease total:{count-1}")
    print("Done disease.")
    return text_dict

def get_operation_data(urls:list,headers:list) -> dict:
    '''爬取手术页面的数据'''
    print("Fetching operation data...")
    html_list=[]
    html_list_final=[]
    html_record=[]
    text_dict={"total":0,"contents":[],"disease_html":[]}
    count_page=1
    for url in urls:
        html=get_html(url,headers[randint(0,18)])
        content_html_list=get_content_html(html)
        for item in content_html_list:
            html_list.append(item)
        print(f'Page {count_page} getted.')
        count_page+=1
    for url_tuple in html_list:
        if(url_tuple[0] not in html_record):
            html_list_final.append(url_tuple)
            html_record.append(url_tuple[0])
    html_list=html_list_final
    # html_list=list(set(html_list))
    print(html_list)
    print('Operation HTMLs getted.')
    sleep(15)
    count=1
    block_list=[]
    for url in html_list:
        try:
            content=get_operation_text(url,headers[randint(0,18)])
            text_dict["total"]+=1
            text_dict["contents"].append(content["content"])
            text_dict["disease_html"].extend(text_dict["disease_html"])
            print(count,':',text_dict["contents"][-1])
            count+=1
        except Exception as e:
            print(f"{url} Request blocked, next url.")
            block_list.append(url)
            continue
    print(f"Unblocked total:{count-1}")
    print("Wait for 5 seconds.")
    #等待15秒
    sleep(15)
    # sleep(150)
    for url in block_list:
        try:
            content=get_operation_text(url,headers[0])
            text_dict["total"]+=1
            text_dict["contents"].append(content["content"])
            text_dict["disease_html"].extend(text_dict["disease_html"])
            print(count,':',text_dict["contents"][-1])
            count+=1
        except Exception as e:
            print(f"{url} Request blocked, next url.")
            continue
    print(f"Operation total:{count-1}")
    print("Done operation.")
    return text_dict

def spiderMain(urls:dict,header:list) -> dict:
    disease_outer_urls=[]
    data_dict={"disease":[],"symptom":[],"test":[],"operation":[]}
    symptom_data=get_symptom_data(urls["symptom"],header)
    data_dict["symptom"].extend(symptom_data["contents"])
    disease_outer_urls.extend(symptom_data["disease_html"])
    sleep(15)
    test_data=get_test_data(urls["test"],header)
    data_dict["test"].extend(test_data["contents"])
    disease_outer_urls.extend(test_data["disease_html"])
    sleep(15)
    operation_data=get_operation_data(urls["operation"],header)
    data_dict["operation"].extend(operation_data["contents"])
    disease_outer_urls.extend(operation_data["disease_html"])
    sleep(15)
    disease_outer_urls=[]
    disease_data=get_disease_data(urls["disease"],disease_outer_urls,header)
    data_dict["disease"].extend(disease_data["contents"])

    return data_dict

if __name__=="__main__":
    urls={
        "disease":["https://jbk.39.net/bw/t1_p{}/key=%E7%B3%96%E5%B0%BF%E7%97%85".format(str(i)) for i in range(1,15)],
        "symptom":["https://jbk.39.net/bw/t2_p{}/key=%e7%b3%96%e5%b0%bf%e7%97%85".format(str(i)) for i in range(1,8)],
        "test":["https://jbk.39.net/bw/t3_p{}/key=%e7%b3%96%e5%b0%bf%e7%97%85".format(str(i)) for i in range(1,9)],
        "operation":["https://jbk.39.net/bw/t4_p{}/key=%e7%b3%96%e5%b0%bf%e7%97%85".format(str(i)) for i in range(1,3)]
        }
    # urls={
    #     "disease":["https://jbk.39.net/bw/t1_p1/key=%E7%B3%96%E5%B0%BF%E7%97%85".format(str(i)) for i in range(1,2)],
    #     "symptom":["https://jbk.39.net/bw/t2_p1/key=%e7%b3%96%e5%b0%bf%e7%97%85".format(str(i)) for i in range(1,2)],
    #     "test":["https://jbk.39.net/bw/t3_p1/key=%e7%b3%96%e5%b0%bf%e7%97%85".format(str(i)) for i in range(1,2)],
    #     "operation":["https://jbk.39.net/bw/t4_p1/key=%e7%b3%96%e5%b0%bf%e7%97%85".format(str(i)) for i in range(1,2)]
    #     }
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

    data_dict=spiderMain(urls,headers)
    with open(os.getcwd()+"/graph/data/spiderData/knowledge.json","w",encoding="utf-8") as fp:
        json.dump(data_dict,fp,ensure_ascii=False)

    # print(getText("https://jbk.39.net/wjlwlzhz/",headers=headers[-2],decode="utf-8"))

    # print(getText("https://jbk.39.net/tnb/",headers=headers[-1],decode="utf-8"))
    # req=urllib.request.Request(url="https://jbk.39.net/bw/",headers={"User-Agent": "Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/109.0.0.0Safari/537.36"})
    # req=urllib.request.Request(url="https://jbk.39.net/bw/",headers={"User-Agent":"Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,like Gecko)Chrome/122.0.0.0 Safari/537.36"})
    # res=urllib.request.urlopen(req)
    # html=res.read()
    # print(html)
    # html=getHTML("https://jbk.39.net/bw/t1_p1/key=%E7%B3%96%E5%B0%BF%E7%97%85",headers[randint(0,18)])
    # print(getText("https://jbk.39.net/tnb/",headers[0]))