import os
from configparser import ConfigParser
import flask
import secrets

class APPConfig(flask.Config):
    DEBUG=False
    TESTING=False
    SECRET_KEY=secrets.token_hex(16)
    SESSION_TYPE='filesystem'
    SESSION_PERMANENT=False
    SESSION_USE_SIGNER=False
    SESSION_COOKIE_NAME='unique_session_cookie'
    SESSION_FILE_MODE=384
    SESSION_KEY_PREFIX='session'
    SESSION_FILE_DIR='/session'
    MAX_COOKIE_SIZE=8192

#web应用程序使用
class WebConfig:
    def __init__(self,config_dir:str) -> None:
        self.config=ConfigParser()
        self.config.read(config_dir,encoding='utf8')
        self.sql_host=self.config.get('sql','host')
        self.sql_port=eval(self.config.get('sql','port'))
        self.sql_user=self.config.get('sql','user')
        self.sql_password=self.config.get('sql','password')
        self.sql_db=self.config.get('sql','db')
        self.app_host=self.config.get('app','host')
        self.app_port=eval(self.config.get('app','port'))
        self.app_admin=self.config.get('app','admin')
        self.app_cert_dir=os.getcwd()+self.config.get('app','cert_dir')
        self.app_key_dir=os.getcwd()+self.config.get('app','key_dir')
        self.app_service_num=eval(self.config.get('app','service_num'))
        self.app_data_num=eval(self.config.get('app','data_num'))

    def get_config(self) -> ConfigParser:
        return self.config

def has_alpha(word:str) -> bool:
    alphabet=set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    for char in word:
        if(char in alphabet):
            return True
    return False

def is_sub_string(string:str,traget_string:str) -> tuple:
    '''判断某一字符串是否为另一字符串的子串'''
    if(string in traget_string):
        return abs(len(traget_string)-len(string)),True
    return None,False
    
def check_email_format(email:str) -> bool:
    if(email.find('@')==-1):
        return False
    suffix=email.split('@')[1].strip()
    if(suffix==''):
        return False
    suffix_list=suffix.split('.')
    for s in suffix_list:
        if(s==''):
            return False
    return True

def check_password_format(password:str,password_again:str) -> tuple:
    if(len(password)<8):
        return False,'密码过短！'
    if(len(password)>20):
        return False,'密码过长！'
    legal=set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789*_@&')
    for char in password:
        if(char not in legal):
            return False,"密码中出现非法字符！"
    if(password!=password_again):
        return False,'两次输入的密码不相同！'
    return True,None

def register_check(form:dict) -> tuple:
    email=form["email"]
    password=form["password"]
    password_again=form["password_again"]
    if(not check_email_format(email)):
        return False,'邮箱格式错误！'
    result=check_password_format(password,password_again)
    if(not result[0]):
        return False,result[1]
    return True,email,password

def read_node(token:str,data:dict) -> dict:
    id=data[f"id({token})"]
    try:
        label=data[f"labels({token})"][0]
    except:
        label='unknown'
    name=data[f"{token}.name"]
    return {"id":id,"label":label,"name":name}

def read_relation(data:dict) -> dict:
    source=data["id(m)"]
    target=data["id(n)"]
    name=data["r.name"]
    return {"source":source,"target":target,"name":name}

def read_graph_data(data_list:list):
    ids=[]
    nodes=[]
    links=[]
    for data in data_list:
        m=read_node('m',data)
        n=read_node('n',data)
        if(m["id"] not in ids):
            nodes.append(m)
            ids.append(m["id"])
        if(n["id"] not in ids):
            nodes.append(n)
            ids.append(n["id"])
        links.append(read_relation(data))
    return {"nodes":nodes,"links":links}

def read_single_graph_data(data_list:list):
    ids=[]
    nodes=[]
    for data in data_list:
        n=read_node('n',data)
        if(n["id"] not in ids):
            nodes.append(n)
            ids.append(n["id"])
    return {"nodes":nodes,"links":[]}
