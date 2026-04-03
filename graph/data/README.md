# 记录

## 记录1

### 记录说明

数据文件**6.json**被修正过，因为其中出现了不在关系列表中的关系“ADE_Disease”。  
该关系仅存在与此数据文件中，暂时认为是开源此数据集的团队在进行实体、关系抽取与数据标注时的错误。  
该关系被修正为存在于关系列表中的关系“ADE_Drug”。  
**由于修正数据工作量较大，因此暂时放弃修正**

### 附加内容

建立图谱时的错误日志如下：
2023-10-25 21:43:42,947 - buildMedicalGraph.py[line:173] - ERROR: Set relation failed! Relation is: {'relation_type': 'ADE_Disease', 'relation_id': 'R288', 'head_entity_id': 'T568', 'tail_entity_id': 'T564'}, i is 6.
2023-10-25 21:43:42,947 - buildMedicalGraph.py[line:173] - ERROR: Set relation failed! Relation is: {'relation_type': 'ADE_Disease', 'relation_id': 'R352', 'head_entity_id': 'T684', 'tail_entity_id': 'T679'}, i is 6.
