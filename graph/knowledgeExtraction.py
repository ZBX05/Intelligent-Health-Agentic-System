import os
import json
from knowledgeSpider import spiderMain

def extract(data_dir:str,target_dir:str) -> None:
    with open(data_dir,"r",encoding="utf-8",errors="ignore") as fp:
        data=json.load(fp)
    knowledge={
        "entity":{
            "disease":[],
            "symptom":[],
            "test":[],
            "drug":[],
            "anatomy":[],
            "department":[],
            "infectivity":[],
            "operation":[],
            "period":[]
        },
        "relation":{
            "anatomy_disease":[],
            "drug_disease":[],
            "symptom_disease":[],
            "test_disease":[],
            "operation_disease":[],
            "department_disease":[],
            "infectivity_disease":[],
            "period_disease":[]
        }
    }

    for item in data.keys():
        for d in data[item]:
            for key in d.keys():
                if(key in knowledge["entity"].keys() and isinstance(d[key],list)):
                    knowledge["entity"][key].extend(d[key])
                elif(key in knowledge["entity"].keys() and not isinstance(d[key],list)):
                    knowledge["entity"][key].append(d[key])
                elif(key in knowledge["relation"].keys()):
                    knowledge["relation"][key].extend(d[key])
                if(item=="disease" and key!="disease"):
                    knowledge["relation"][key+"_disease"].extend([[e,d["disease"]] for e in d[key]])
        for key in knowledge["entity"].keys():
            knowledge["entity"][key]=list(set(knowledge["entity"][key]))
        with open(target_dir,"w",encoding="utf-8") as fp:
            json.dump(knowledge,fp,ensure_ascii=False)

if __name__=="__main__":
    urls={
        "disease":["https://jbk.39.net/bw/t1_p{}/key=%E7%B3%96%E5%B0%BF%E7%97%85".format(str(i)) for i in range(1,15)],
        "symptom":["https://jbk.39.net/bw/t2_p{}/key=%e7%b3%96%e5%b0%bf%e7%97%85".format(str(i)) for i in range(1,8)],
        "test":["https://jbk.39.net/bw/t3_p{}/key=%e7%b3%96%e5%b0%bf%e7%97%85".format(str(i)) for i in range(1,9)],
        "operation":["https://jbk.39.net/bw/t4_p{}/key=%e7%b3%96%e5%b0%bf%e7%97%85".format(str(i)) for i in range(1,3)]
        }
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
    
    extract(os.getcwd()+"/graph/data/spiderData/knowledge.json",os.getcwd()+"/graph/data/extractedData/extracted.json")