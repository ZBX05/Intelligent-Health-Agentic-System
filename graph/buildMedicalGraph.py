#建立图谱
import os
import logging
import json
from py2neo import Graph,Node
# import jieba
from manuallyCorrect import correct
from dotenv import load_dotenv

load_dotenv("./.env")
neo4j_url = os.getenv("NEO4J_BROSWER_URL")
neo4j_username = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")

class MedicalGraph:
    def __init__(self,data_path:str,knowledge_data_dir:str) -> None:
        self.data_path=data_path
        self.knowledge_data_dir=knowledge_data_dir
        self.stop_words_dir=""
        self.g = Graph(
            host=neo4j_url,
            user=neo4j_username,
            password=neo4j_password)
    
    def set_dicts_dir(self,disease_dict_dir_list:list=[]) -> None:
        self.disease_dict_dir=disease_dict_dir_list
    
    def set_stopwords_dir(self,stop_words_dir:str) -> None:
        self.stop_words_dir=stop_words_dir

    #清空图数据库中所有的内容 
    def clear_all(self) -> None:
        try:
            self.g.delete_all()
        except Exception as e:
            print(e)
    
    def read_knowledge_data(self) -> dict:
        with open(self.knowledge_data_dir,"r",encoding="utf-8",errors="ignore") as fp:
            knowledge_data=json.load(fp)
        return knowledge_data

    #读取节点
    def read_data(self) -> tuple:
        #实体列表
        disease=[]
        Class=[]
        reason=[]
        pathogenesis=[]
        symptom=[]
        test=[]
        test_items=[]
        test_value=[]
        drug=[]
        frequency=[]
        amount=[]
        method=[]
        treatment=[]
        operation=[]
        ade=[]
        anatomy=[]
        level=[]
        duration=[]
        department=[]
        infectivity=[]
        period=[]

        #关系列表
        department_disease=[]
        infectivity_disease=[]
        period_disease=[]
        test_items_disease=[]
        treatment_disease=[]
        class_disease=[]
        anatomy_disease=[]
        drug_disease=[]
        reason_disease=[]
        symptom_disease=[]
        operation_disease=[]
        test_disease=[]
        pathogenesis_disease=[]
        ade_drug=[]
        amount_drug=[]
        method_drug=[]
        frequency_drug=[]
        duration_drug=[]

        def set_entity(entity_type:str,entity_value:str) -> bool:
            # if(entity_value.find("(")!=-1):
            #     entity_value==entity_value.split("(")[0]
            # else:
            #     pass
            if(entity_type=="Disease"):
                if(entity_value.find("(" or "（")!=-1):
                    entity_value=entity_value.split("(" or "（")[0]
                    # disease.append(entity_value.split("(" or "（")[0])
                else:
                    pass
                entity_value=entity_value.replace(" ","")
                disease.append(entity_value)
            elif(entity_type=="Class"):
                entity_value=entity_value.replace(" ","")
                Class.append(entity_value)
            elif(entity_type=="Reason"):
                reason.append(entity_value)
            elif(entity_type=="Pathogenesis"):
                pathogenesis.append(entity_value)
            elif(entity_type=="Symptom"):
                symptom.append(entity_value)
            elif(entity_type=="Test"):
                test.append(entity_value)
            elif(entity_type=="Test_items"):
                test_items.append(entity_value)
            elif(entity_type=="Test_Value"):
                test_value.append(entity_value)
            elif(entity_type=="Drug"):
                drug.append(entity_value)
            elif(entity_type=="Frequency"):
                frequency.append(entity_value)
            elif(entity_type=="Amount"):
                amount.append(entity_value)
            elif(entity_type=="Method"):
                method.append(entity_value)
            elif(entity_type=="Treatment"):
                treatment.append(entity_value)
            elif(entity_type=="Operation"):
                operation.append(entity_value)
            elif(entity_type=="ADE"):
                ade.append(entity_value)
            elif(entity_type=="Anatomy"):
                anatomy.append(entity_value)
            elif(entity_type=="Level"):
                level.append(entity_value)
            elif(entity_type=="Duration"):
                duration.append(entity_value)
            else:
                return False
            return True
        
        def get_entity(entity_id:str,entities:list) -> str|None:
            for entity in entities:
                if(entity["entity_id"]==entity_id):
                    return entity["entity"]
            return None
        
        def set_relation(relation_type:str,head_entity:str,tail_entity:str) -> bool:
            if(relation_type.find("Disease")!=-1):
                if(tail_entity.find("(" or "（")!=-1):
                    tail_entity=tail_entity.split("(" or "（")[0]
                else:
                    pass
                tail_entity=tail_entity.replace(" ","")
            else:
                pass
            if(relation_type=="Test_items_Disease"):
                test_items_disease.append([head_entity,tail_entity])
            elif(relation_type=="Treatment_Disease"):
                treatment_disease.append([head_entity,tail_entity])
            elif(relation_type=="Class_Disease"):
                head_entity=head_entity.replace(" ","")
                class_disease.append([head_entity,tail_entity])
            elif(relation_type=="Anatomy_Disease"):
                anatomy_disease.append([head_entity,tail_entity])
            elif(relation_type=="Drug_Disease"):
                drug_disease.append([head_entity,tail_entity])
            elif(relation_type=="Reason_Disease"):
                reason_disease.append([head_entity,tail_entity])
            elif(relation_type=="Symptom_Disease"):
                symptom_disease.append([head_entity,tail_entity])
            elif(relation_type=="Operation_Disease"):
                operation_disease.append([head_entity,tail_entity])
            elif(relation_type=="Test_Disease"):
                test_disease.append([head_entity,tail_entity])
            elif(relation_type=="Pathogenesis_Disease"):
                pathogenesis_disease.append([head_entity,tail_entity])
            elif(relation_type=="ADE_Drug"):
                ade_drug.append([head_entity,tail_entity])
            elif(relation_type=="Amount_Drug"):
                amount_drug.append([head_entity,tail_entity])
            elif(relation_type=="Method_Drug"):
                method_drug.append([head_entity,tail_entity])
            elif(relation_type=="Frequency_Drug"):
                frequency_drug.append([head_entity,tail_entity])
            elif(relation_type=="Duration_Drug"):
                duration_drug.append([head_entity,tail_entity])
            else:
                return False
            return True

        logging.basicConfig(level=logging.WARNING,filename=os.getcwd()+"/log/buildMedicalGraphLog.log",filemode="w",
                            format="%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        print("开始读取")
        for i in range (1,42):#对于每一个json文件进行读取
            # print(f"doc:{i}")
            dir=f"{self.data_path}/{i}.json"
            # dir="./data/sample.json"
            with open(dir,"r",encoding="utf-8",errors="ignore") as data:
                data_json=json.load(data)
            paragraphs=data_json["paragraphs"]
            for paragraph in paragraphs:#获取文段
                sentences=paragraph["sentences"]
                for sentence in sentences:#获取句子
                    entities=sentence["entities"]
                    relations=sentence["relations"]
                    for entity in entities:#读取实体
                        entity_type=entity["entity_type"]
                        entity_value=entity["entity"]
                        if(not set_entity(entity_type,entity_value)):#读取实体时出错
                            # print(f"Set entity failed! Entity is: {entity}, i is {i}.")
                            logging.error(f"Set entity failed! Entity is: {entity}, i is {i}.")
                    for relation in relations:#读取关系
                        relation_type=relation["relation_type"]
                        head_entity=get_entity(relation["head_entity_id"],entities)
                        tail_entity=get_entity(relation["tail_entity_id"],entities)
                        if(not set_relation(relation_type,head_entity,tail_entity)):#读取关系时出错
                            # print(f"Set relation failed! Relation is: {relation}, i is {i}.")
                            logging.error(f"Set relation failed! Relation is: {relation}, i is {i}.")
            data.close()

        knowledge_data=self.read_knowledge_data()
        # disease.extend(knowledge_data["entity"]["disease"])
        # symptom.extend(knowledge_data["entity"]["symptom"])
        # test.extend(knowledge_data["entity"]["test"])
        # drug.extend(knowledge_data["entity"]["drug"])
        # anatomy.extend(knowledge_data["entity"]["anatomy"])
        # department.extend(knowledge_data["entity"]["department"])
        # anatomy_disease.extend(knowledge_data["relation"]["anatomy_disease"])
        # drug_disease.extend(knowledge_data["relation"]["drug_disease"])
        # symptom_disease.extend(knowledge_data["relation"]["symptom_disease"])
        # test_disease.extend(knowledge_data["relation"]["test_disease"])
        # department_disease.extend(knowledge_data["relation"]["department_disease"])

        disease_=knowledge_data["entity"]["disease"]
        symptom_=knowledge_data["entity"]["symptom"]
        test_=knowledge_data["entity"]["test"]
        drug_=knowledge_data["entity"]["drug"]
        anatomy_=knowledge_data["entity"]["anatomy"]
        operation_=knowledge_data["entity"]["operation"]
        department_=knowledge_data["entity"]["department"]
        infectivity_=knowledge_data["entity"]["infectivity"]
        period_=knowledge_data["entity"]["period"]
        anatomy_disease_=knowledge_data["relation"]["anatomy_disease"]
        drug_disease_=knowledge_data["relation"]["drug_disease"]
        symptom_disease_=knowledge_data["relation"]["symptom_disease"]
        test_disease_=knowledge_data["relation"]["test_disease"]
        department_disease_=knowledge_data["relation"]["department_disease"]
        operation_disease_=knowledge_data["relation"]["operation_disease"]
        infectivity_disease_=knowledge_data["relation"]["infectivity_disease"]
        period_disease_=knowledge_data["relation"]["period_disease"]
        
        # extracted_entity_set,extracted_relation_group_list=entity_align()

        # disease_=extracted_entity_set[0]
        # drug_=extracted_entity_set[1]
        # test_=extracted_entity_set[2]
        # anatomy_=extracted_entity_set[3]
        # symptom_=extracted_entity_set[4]
        # department_=extracted_entity_set[5]
        # operation_=extracted_entity_set[6]
        # infectivity_=extracted_entity_set[7]
        # period_=extracted_entity_set[8]
        # symptom_disease_=extracted_relation_group_list[0]
        # anatomy_disease_=extracted_relation_group_list[1]
        # drug_disease_=extracted_relation_group_list[2]
        # test_disease_=extracted_relation_group_list[3]
        # department_disease_=extracted_relation_group_list[4]
        # operation_disease_=extracted_relation_group_list[5]
        # infectivity_disease_=extracted_relation_group_list[6]
        # period_disease_=extracted_relation_group_list[7]

        disease.extend(disease_)
        symptom.extend(symptom_)
        test.extend(test_)
        drug.extend(drug_)
        anatomy.extend(anatomy_)
        department.extend(department_)
        operation.extend(operation_)
        infectivity.extend(infectivity_)
        period.extend(period_)
        anatomy_disease.extend(anatomy_disease_)
        drug_disease.extend(drug_disease_)
        symptom_disease.extend(symptom_disease_)
        test_disease.extend(test_disease_)
        operation_disease.extend(operation_disease_)
        department_disease.extend(department_disease_)
        infectivity_disease.extend(infectivity_disease_)
        period_disease.extend(period_disease_)
        
        print("读取完成")
        return set(reason),set(infectivity),set(period),set(disease),set(Class),set(pathogenesis),set(symptom),set(test),\
            set(test_items),set(test_value),set(drug),\
            set(frequency),set(amount),set(method),set(treatment),set(operation),set(ade),set(anatomy),set(level),set(duration),\
            set(department),\
            reason_disease,infectivity_disease,period_disease,symptom_disease,pathogenesis_disease,anatomy_disease,class_disease,\
            test_items_disease,treatment_disease,\
            drug_disease,operation_disease,test_disease,ade_drug,amount_drug,method_drug,frequency_drug,duration_drug,\
            department_disease

    #建立一个节点
    def create_node(self,label:str,nodes:set) -> None:
        count=0
        for node_name in nodes:
            node=Node(label,name=node_name)
            self.g.create(node)
            count+=1
            print(count)

    def add_property(self,property:str,entity_dict_list:list,property_set:set) -> None:
        count=0
        for rel in property_set:
            for e in entity_dict_list:
                if(e["name"]==rel[1]):
                    e[property].add(rel[0])
                    count+=1
                    break
            print(count)
    
    def create_disease_node(self,label:str,nodes:list) -> None:
        count=0
        for node_dict in nodes:
            node=Node(label,name=node_dict["name"],reason=list(node_dict["reason"])
                      ,infectivity=list(node_dict["infectivity"]),period=list(node_dict["period"]))
            # node=Node(label,name=node_dict["name"])
            self.g.create(node)
            count+=1
            print(count)
    
    #建立所有节点
    def create_graph_nodes(self,data:tuple) -> None:
        reason,infectivity,period,disease,Class,pathogenesis,symptom,test,test_items,_,drug,frequency,amount,method,treatment,\
            operation,ade,anatomy,_,duration,department,reason_disease,infectivity_disease,period_disease,_,_,\
            _,_,_,_,_,_,_,_,_,_,_,_,_,=data
        
        disease_dict_list=[{"name":d,"reason":set(),"infectivity":set(),"period":set()} for d in disease]

        # self.add_property("symptom",disease_dict_list,symptom_disease)
        # print("Property: symptom")
        self.add_property("reason",disease_dict_list,reason_disease)
        print("Property: reason")
        self.add_property("infectivity",disease_dict_list,infectivity_disease)
        print("Property: infectivity")
        self.add_property("period",disease_dict_list,period_disease)
        print("Property: period")
        # # self.add_property("pathogenesis",disease_dict_list,pathogenesis_disease)
        # # print("Property: pathogenesis")
        # self.add_property("anatomy",disease_dict_list,anatomy_disease)
        # print("Property: anatomy")

        self.create_disease_node("Disease",disease_dict_list)
        f_disease=open(os.getcwd()+"/txt/disease.txt", "w+",encoding="utf-8")
        f_disease.write("\n".join(list(disease)))
        f_disease.close()
        print("Disease:",len(disease))
        
        self.create_node("Class",Class)
        f_class=open(os.getcwd()+"/txt/class.txt", "w+",encoding="utf-8")
        f_class.write("\n".join(list(Class)))
        f_class.close()
        print("Class:",len(Class))
        
        # self.create_node("Infectivity",infectivity)
        f_duration=open(os.getcwd()+"/txt/infectivity.txt", "w+",encoding="utf-8")
        f_duration.write("\n".join(list(infectivity)))
        f_duration.close()
        print("Infectivity:",len(infectivity))

        # self.create_node("Period",period)
        f_duration=open(os.getcwd()+"/txt/period.txt", "w+",encoding="utf-8")
        f_duration.write("\n".join(list(period)))
        f_duration.close()
        print("Period:",len(period))

        # self.create_node("Reason",reason)
        f_reason=open(os.getcwd()+"/txt/reason.txt", "w+",encoding="utf-8")
        f_reason.write("\n".join(list(reason)))
        f_reason.close()
        print("Reason:",len(reason))

        self.create_node("Pathogenesis",pathogenesis)
        f_pathogenesis=open(os.getcwd()+"/txt/pathogenesis.txt", "w+",encoding="utf-8")
        f_pathogenesis.write("\n".join(list(pathogenesis)))
        f_pathogenesis.close()
        print("Pathogenesis:",len(pathogenesis))

        self.create_node("Symptom",symptom)
        f_symptom=open(os.getcwd()+"/txt/symptom.txt", "w+",encoding="utf-8")
        f_symptom.write("\n".join(list(symptom)))
        f_symptom.close()
        print("Symptom:",len(symptom))

        self.create_node("Test",test)
        f_test=open(os.getcwd()+"/txt/test.txt", "w+",encoding="utf-8")
        f_test.write("\n".join(list(test)))
        f_test.close()
        print("Test:",len(test))

        self.create_node("Test_items",test_items)
        f_test_items=open(os.getcwd()+"/txt/test_items.txt", "w+",encoding="utf-8")
        f_test_items.write("\n".join(list(test_items)))
        f_test_items.close()
        print("Test_items:",len(test_items))

        # self.create_node("Test_Value",test_value)
        # f_test_value=open(os.getcwd()+"/txt/test_value.txt", "w+",encoding="utf-8")
        # f_test_value.write("\n".join(list(test_value)))
        # f_test_value.close()
        # print("Test_Value:",len(test_value))

        self.create_node("Drug",drug)
        f_drug=open(os.getcwd()+"/txt/drug.txt", "w+",encoding="utf-8")
        f_drug.write("\n".join(list(drug)))
        f_drug.close()
        print("Drug:",len(drug))
        
        self.create_node("Frequency",frequency)
        f_frequency=open(os.getcwd()+"/txt/frequency.txt", "w+",encoding="utf-8")
        f_frequency.write("\n".join(list(frequency)))
        f_frequency.close()
        print("Frequency:",len(frequency))
        
        self.create_node("Amount",amount)
        f_amount=open(os.getcwd()+"/txt/amount.txt", "w+",encoding="utf-8")
        f_amount.write("\n".join(list(amount)))
        f_amount.close()
        print("Amount:",len(amount))
        
        self.create_node("Method",method)
        f_method=open(os.getcwd()+"/txt/method.txt", "w+",encoding="utf-8")
        f_method.write("\n".join(list(method)))
        f_method.close()
        print("Method:",len(method))

        self.create_node("Treatment",treatment)
        f_treatment=open(os.getcwd()+"/txt/treatment.txt", "w+",encoding="utf-8")
        f_treatment.write("\n".join(list(treatment)))
        f_treatment.close()
        print("Treatment:",len(treatment))
        
        self.create_node("Operation",operation)
        f_operation=open(os.getcwd()+"/txt/operation.txt", "w+",encoding="utf-8")
        f_operation.write("\n".join(list(operation)))
        f_operation.close()
        print("Operation:",len(operation))

        self.create_node("ADE",ade)
        f_ade=open(os.getcwd()+"/txt/ade.txt", "w+",encoding="utf-8")
        f_ade.write("\n".join(list(ade)))
        f_ade.close()
        print("ADE:",len(ade))

        self.create_node("Anatomy",anatomy)
        f_anatomy=open(os.getcwd()+"/txt/anatomy.txt", "w+",encoding="utf-8")
        f_anatomy.write("\n".join(list(anatomy)))
        f_anatomy.close()
        print("Anatomy:",len(anatomy))

        # self.create_node("Level",level)
        # f_level=open(os.getcwd()+"/txt/level.txt", "w+",encoding="utf-8")
        # f_level.write("\n".join(list(level)))
        # f_level.close()
        # print("Level:",len(level))

        self.create_node("Duration",duration)
        f_duration=open(os.getcwd()+"/txt/duration.txt", "w+",encoding="utf-8")
        f_duration.write("\n".join(list(duration)))
        f_duration.close()
        print("Duration:",len(duration))

        self.create_node("Department",department)
        f_department=open(os.getcwd()+"/txt/department.txt", "w+",encoding="utf-8")
        f_department.write("\n".join(list(department)))
        f_department.close()
        print("Department:",len(department))

    #创建一条关联关系
    def create_relationship(self,start_node:str,end_node:str,edges:list,rel_type:str,rel_name:str) -> None:
        count=0
        # 去重处理
        set_edges=[]
        for edge in edges:
            set_edges.append("###".join(edge))
        all=len(set(set_edges))
        for edge in set(set_edges):
            edge = edge.split("###")
            p=edge[0]
            q=edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.g.run(query)
                count += 1
                print(rel_type,count,all)
            except Exception as e:
                print(e)
    
    #创建所有关联关系
    def create_graph_relationship(self,data:tuple) -> None:
        _,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,symptom_disease,pathogenesis_disease,anatomy_disease,class_disease,\
            test_items_disease,treatment_disease,drug_disease,operation_disease,test_disease,ade_drug,amount_drug,method_drug,\
                frequency_drug,duration_drug,department_disease=data
        self.create_relationship("Test_items","Disease",test_items_disease,"Test_items_Disease","疾病检查指标")
        self.create_relationship("Treatment","Disease",treatment_disease,"Treatment_Disease","疾病治疗方法")
        self.create_relationship("Class","Disease",class_disease,"Class_Disease","疾病类型")
        self.create_relationship("Anatomy","Disease",anatomy_disease,"Anatomy_Disease","病变部位")
        self.create_relationship("Drug","Disease",drug_disease,"Drug_Disease","有效药物")
        self.create_relationship("Department","Disease",department_disease,"Department_Disease","疾病挂号科室")
        # self.create_relationship("Reason","Disease",reason_disease,"Reason_Disease","疾病病因")
        self.create_relationship("Symptom","Disease",symptom_disease,"Symptom_Disease","疾病症状")
        self.create_relationship("Operation","Disease",operation_disease,"Operation_Disease","需进行的手术")
        self.create_relationship("Test","Disease",test_disease,"Test_Disease","疾病检查方法")
        self.create_relationship("Pathogenesis","Disease",pathogenesis_disease,"Pathogenesis_Disease","疾病发病机制")
        self.create_relationship("ADE","Drug",ade_drug,"ADE_Drug","药物不良反应")
        self.create_relationship("Amount","Drug",amount_drug,"Amount_Drug","药物使用剂量")
        self.create_relationship("Method","Drug",method_drug,"Method_Drug","药物使用方法")
        self.create_relationship("Frequency","Drug",frequency_drug,"Frequency_Drug","药物使用频率")
        self.create_relationship("Duration","Drug",duration_drug,"Duration_Drug","药物持续使用时间")
    
        
if __name__=="__main__":
    handler=MedicalGraph(os.getcwd()+"/data/diakg/0521_new_format",os.getcwd()+"/data/extractedData/extracted.json")
    handler.set_dicts_dir([os.getcwd()+"/txt/disease.txt",os.getcwd()+"/dict/THUOCL_medical.txt"])
    handler.set_stopwords_dir(os.getcwd()+"/dict/stopwords.txt")
    print("=======清空图数据库=======")
    handler.clear_all()
    print("step1:读取数据中")
    data=handler.read_data()
    print("step3:导入图谱节点")
    handler.create_graph_nodes(data)
    print("step4:导入图谱边")
    handler.create_graph_relationship(data)
    correct()
    print("知识图谱构建完成")