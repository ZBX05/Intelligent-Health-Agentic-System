from typing import Any
from transformers import BertTokenizer
import os
import torch
from functionsAndClasses import *
from model import NERModel,IRModel
import numpy as np

def get_entity_list(tokens:list,predictions_in_char:list) -> list:
    '''将token列表中属于同一命名实体的token进行拼接，并获得包含完整命名实体的列表'''
    entity_list=[]
    entity_dict={
        "dise":[],
        "symp":[],
        "drug":[],
        "chec":[],
        "cure":[],
        "body":[]
    }
    for idx in range(0,len(tokens)):
        if(predictions_in_char[idx]!='O'):
            head=predictions_in_char[idx].split('-')[0]
            key=predictions_in_char[idx].split('-')[1]
            entity_dict[key].append((tokens[idx],head))
    for key in entity_dict.keys():
        if(len(entity_dict[key])!=0):
            kind_list=entity_dict[key]
            this_entity=[kind_list[0][0].replace('#',''),key]
            for idx in range(1,len(kind_list)):
                if kind_list[idx][1]=='B':
                    entity_list.append(tuple(this_entity))
                    this_entity=[kind_list[idx][0].replace('#',''),key]
                else:
                    this_entity[0]+=kind_list[idx][0].replace('#','')
            if(len(entity_list)==0 or entity_list[-1]!=tuple(this_entity)):
                entity_list.append(tuple(this_entity))
    return entity_list

def get_entities(model:NERModel,tokenizer:BertTokenizer,tokenizer_max_length:int,input_text:str,ids_to_labels:dict,
                 ids_padding_value:int) -> dict:
    '''问句命名实体识别'''
    output_dict={}
    output_dict["input_text"]=input_text
    tokenized_input=tokenizer(input_text,max_length=tokenizer_max_length,truncation=True,return_tensors="pt")
    output_dict["input_ids"]=tokenized_input["input_ids"][0].tolist()
    output_dict["tokens"]=tokenizer.convert_ids_to_tokens(tokenized_input["input_ids"][0])[1:-1]
    input_ids=np.zeros((1,len(output_dict["input_ids"])))
    input_ids[0][:]=output_dict["input_ids"]
    padding_starts=[len(output_dict["input_ids"])%tokenizer_max_length]
    input_ids=torch.tensor(input_ids,dtype=torch.long,device='cpu')
    padding_starts=torch.tensor(padding_starts,dtype=torch.long,device='cpu')
    masks=input_ids.gt(ids_padding_value).to('cpu')
    logits,=model(input_ids=input_ids,attention_mask=masks,labels=None,padding_starts=padding_starts)
    preds=logits.argmax(dim=2)
    output_dict["predictions"]=preds[0].tolist()
    char_preds=[]
    for label in preds[0].tolist():
        char_preds.append(ids_to_labels[label])
    output_dict["predictions_in_char"]=char_preds
    output_dict["predictions_as_entity_list"]=get_entity_list(output_dict["tokens"],output_dict["predictions_in_char"])
    return output_dict

def get_intention(model:IRModel,tokenizer:BertTokenizer,tokenizer_max_length:int,input_text:str,intentions_dict:dict,
                  ids_padding_value:int) -> dict:
    '''问句意图识别'''
    if(len(input_text)>tokenizer_max_length):
            input_text=input_text[len(input_text)-tokenizer_max_length:]
    output_dict={}
    output_dict["input_text"]=input_text
    tokenized_input=tokenizer(input_text,max_length=tokenizer_max_length,truncation=True,return_tensors="pt")
    ids=tokenized_input["input_ids"][0].tolist()
    input_ids=np.zeros((1,len(ids)))
    input_ids[0][:]=ids
    input_ids=torch.tensor(input_ids,dtype=torch.long,device='cpu')
    masks=input_ids.gt(ids_padding_value).to('cpu')
    logits=model(input_ids=input_ids,attention_mask=masks)
    pred=logits.argmax().tolist()
    output_dict["prediction"]=pred
    output_dict["prediction_in_char"]=intentions_dict[pred]
    return output_dict

def named_entities_recognize(model:NERModel|IRModel,tokenizer:BertTokenizer,tokenizer_max_length:int,input_text:str,mapping_dict:dict,
                  ids_padding_value:int,mode:str='usr') -> dict:
    '''问句命名实体识别功能上层接口'''
    if(isinstance(model,NERModel)):
        result_dict=get_entities(model,tokenizer,tokenizer_max_length,input_text,mapping_dict,ids_padding_value)
    else:
        raise TypeError('Unknown model type!')
    if(mode=='usr'):
        return {"predictions_as_entity_list":result_dict["predictions_as_entity_list"]}
    else:
        return result_dict
    
def intention_recognize(model:NERModel|IRModel,tokenizer:BertTokenizer,tokenizer_max_length:int,input_text:str,
                        mapping_dict:dict,ids_padding_value:int,mode:str='usr') -> dict:
    '''问句意图识别功能上层接口'''
    if(isinstance(model,IRModel)):
        result_dict=get_intention(model,tokenizer,tokenizer_max_length,input_text,mapping_dict,ids_padding_value)
    else:
        raise TypeError('Unknown model type!')
    if(mode=='usr'):
        return {"prediction":result_dict["prediction"]}
    else:
        return result_dict
    
def parse_question_text(question_text:str,ner_model:NERModel,ir_model:IRModel,tokenizer:BertTokenizer,ner_max_length:int,
                        ir_max_length:int,ids_to_labels:dict,intentions_dict:dict,ner_padding_value:int,ir_padding_vlaue:int,
                        mode:str='usr') -> dict:
    '''解析问句'''
    if(mode!='usr' and mode!='dev'):
        raise ValueError('Invalid mode specified!')
    if(len(question_text)<=0):
        raise ValueError('Empty input!')
    if(ner_max_length>=ir_max_length):
        max_length=ner_max_length
    else:
        max_length=ir_max_length
    if(len(question_text)>max_length-2):
        raise ValueError('Too many input characters!')
    ner_result=named_entities_recognize(ner_model,tokenizer,ner_max_length,question_text,ids_to_labels,ner_padding_value,mode)
    ir_result=intention_recognize(ir_model,tokenizer,ir_max_length,question_text,intentions_dict,ir_padding_vlaue,mode)
    return {"ner_result":ner_result,"ir_result":ir_result}

class Parser:
    def __init__(self,config_dir:str) -> None:
        #由于社区版neo4j没有权限管理等功能，因此数据库没有任何安全措施，故在此次毕设项目中不考虑为每名用户创建单独neo4j数据库用户
        config=Config(config_dir)
        self.ner_model=create_ner_model_from_config(config)
        self.ir_model=create_ir_model_from_config(config)
        self.tokenizer=BertTokenizer.from_pretrained(config.bert_path)
        self.ids_to_labels=config.ids_to_labels
        self.intentions_dict=config.intentions_dict
        self.ner_max_length=config.ner_max_length
        self.ir_max_length=config.ir_max_length
        self.ner_padding_value=config.ner_ids_padding_value
        self.ir_padding_vlaue=config.ir_ids_padding_value
        self.mode='usr'
    
    def set_mode(self,mode:str='usr') -> None:
        self.mode=mode
    
    def parse(self,question_text) -> dict:
        return parse_question_text(question_text,self.ner_model,self.ir_model,self.tokenizer,self.ner_max_length,self.ir_max_length,
                            self.ids_to_labels,self.intentions_dict,self.ner_padding_value,self.ir_padding_vlaue,self.mode)

    def __call__(self,question_text:str) -> dict:
        return self.parse(question_text)

if __name__=='__main__':
    # print(get_entity_list(['糖', '尿', '病', '肾', '病', '应', '该', '吃', '什', '么', '药'],['B-dise', 'I-dise', 'I-dise', 'I-dise', 'I-dise', 'O', 'O', 'O', 'O', 'O', 'O']))
    # print(get_entity_list(['糖', '尿', '病', '肾', '病', '糖', '尿', '病'],['B-dise', 'I-dise', 'I-dise', 'I-dise', 'I-dise', 'B-dise', 'I-dise', 'I-dise']))
    text='糖尿病的症状'
    # ner_model=create_ner_model('F:\\system\\nlp\\model\\ner\\model_state.pth','f:\\system\\nlp\\model',768,384,13,0.3,0.5,-1,0)
    # ir_model=create_ir_model('F:\\system\\nlp\\model\\ir\\model_state.pth','f:\\system\\nlp\\model',768,384,9,0.5,0)
    tokenizer=BertTokenizer.from_pretrained('f:\\system\\nlp\\model')
    config=Config(os.getcwd()+'\\backend\\config\\config.cfg')
    ner_model=create_ner_model_from_config(config)
    ir_model=create_ir_model_from_config(config)
    ids_to_labels=config.ids_to_labels
    intentions_dict=config.intentions_dict
    ner_max_length=config.ner_max_length
    ir_max_length=config.ir_max_length
    ner_padding_value=config.ner_ids_padding_value
    ir_padding_vlaue=config.ir_ids_padding_value
    mode='dev'
    result=parse_question_text(text,ner_model,ir_model,tokenizer,ner_max_length,ir_max_length,ids_to_labels,intentions_dict,
                               ner_padding_value,ir_padding_vlaue,mode)
    # result=recognize(ner_model,tokenizer,512,text,ids_to_labels,0,'dev')
    print(result)
