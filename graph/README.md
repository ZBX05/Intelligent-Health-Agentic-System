# 知识图谱构建模块  

## 运行顺序

1. 爬取疾病数据：运行 `knowledgeSpider.py`，爬取39健康网的疾病百科数据，存储在 `data/spiderData/knowledge.json` 中；
2. 爬取运动数据：运行 `sportSpider.py`，爬取39健康网的运动数据，存储在 `data/spiderData/sport.json` 中；
3. 手动添加数据：运行 `addSportData.py`，向运动数据爬取结果中添加无法爬取的页面数据；
4. 抽取疾病数据：运行 `knowledgeExtraction.py`，从爬取的疾病数据中抽取实体和关系，存储在 `data/extractedData/extracted.json` 中；
5. 构建知识图谱：运行 `buildMedicalGraph.py`，从最终的抽取数据中构建知识图谱，导入到Neo4j数据库中；
6. 抽取运动知识：运行 `sportExtraction.py`，从爬取的运动数据中抽取实体和关系，存储在 `data/extractedData/sport_extracted.json` 中；
7. 补充运动知识到图谱中：运行 `buildSportGraph.py`，从抽取的运动数据中构建疾病与运动的关系，添加到Neo4j数据库中。

## 目录说明  

```text
graph                                       #知识图谱构建模块根目录
    |- data                                 #数据
        |- diakg                            #瑞金医院糖尿病数据
            1.json
            ...
            41.jon
        |- extractedData
            extracted_sport.json            #经过抽取的运动数据
            extracted.json                  #经过抽取的疾病数据
        |- spiderData
            sport.json                      #从39健康网爬取的运动数据
            knowledge.json                  #从39健康网疾病百科爬取的疾病数据
    |- dict                                 #外部词典（主要用于分词）
        baidu_stopwords.txt
        sport_dict.txt
        stopwords.txt
        THUOCL_medical.txt
    |- log
        |- buildMedicalGraphLog.log         #构建知识图谱脚本程序的debug日志
    |- txt                                  #知识图谱构建过程生成的词典
        ade.txt
        ...
        treatment.txt
    关系.png
    实体.png
    addSportData.py                         #向运动数据爬取结果中添加无法爬取的页面数据
    addSportGraph.py                        #从抽取的运动数据中构建疾病与运动的关系并添加到Neo4j数据库
    buildMedicalGraph.py                    #构建知识图谱的脚本程序
    knowledgeSpider.py                      #爬取疾病数据的爬虫脚本
    knowledgeExtraction.py                  #爬取并抽取疾病数据
    manuallyCorrect.py                      #对个别错误数据进行手动矫正
    sportSpider.py                          #爬取运动数据的爬虫脚本
    sportExtraction.py                      #使用LLM抽取运动数据
```  
