import pymysql as sql
import random

class Database:
    def __init__(self,host:str,port:int,user:str,password:str,target:str) -> None:
        self.host=host
        self.port=port
        self.user=user
        self.password=password
        self.target=target
        try:
            self.db=sql.connect(host=self.host,port=self.port,user=self.user,password=self.password,database=self.target,
                                charset='utf8mb4',autocommit=True)
            self.cursor=self.db.cursor()
        except Exception as e:
            print(f"Error connecting to database: {e}")
            exit()

    def get_sql_info(self) -> tuple:
        return (self.host,self.port,self.user,self.password,self.target)

    def connectDatabase(self,host:str,port:int,user:str,password:str,target:str) -> bool:
        self.host=host
        self.port=port
        self.user=user
        self.password=password
        self.target=target
        try:
            self.db=sql.connect(host=host,port=port,user=user,password=password,database=target,charset='utf8mb4',autocommit=True)
            self.cursor=self.db.cursor()
            return True
        except:
            return False
    
    def ping(self,reconnect=bool) -> None:
        try:
            self.db.ping(reconnect)
        except Exception as e:
            raise e

    def get_user_data(self,email:str) -> tuple|None:
        self.cursor.execute("select * from user where email=%s",(email))
        return self.cursor.fetchone()

    def check_user_email(self,email:str) -> str|None:
        self.cursor.execute("select email from user where email=%s",(email))
        result=self.cursor.fetchone()
        if(result is not None):
            return result[0]
        else:
            return None
    
    def check_user_password(self,email:str,password_need_to_check:str) -> bool:
        self.cursor.execute("select pswd from user where email=%s",(email))
        password=self.cursor.fetchone()[0]
        return True if password_need_to_check==password else False
    
    def set_user_password(self,email:str,password:str) -> None:
        self.cursor.execute("update user set pswd=%s where email=%s",(password,email))
        self.db.commit()

    def set_user_state(self,email:str,user_state:str) -> None:
        self.cursor.execute("update user set user_state=%s where email=%s",(user_state,email))
        self.db.commit()
    
    def create_user(self,email:str,password:str) -> None:
        self.cursor.execute("insert into user(email,pswd) values (%s,%s)",(email,password))
        self.db.commit()

    def create_message(self,email:str,admin:str,send_time:str,content:str) -> None:
        self.cursor.execute("insert into message(email,admin,send_time,content) values (%s,%s,%s,%s)",(email,admin,send_time,content))
        self.db.commit()

    def get_message(self,admin:str) -> tuple:
        self.cursor.execute("select * from message where admin=%s order by send_time desc",(admin))
        return self.cursor.fetchall()
    
    def get_message_unread(self,admin:str) -> tuple:
        self.cursor.execute("select * from message where admin=%s and is_read=0 order by send_time desc",(admin))
        return self.cursor.fetchall()
    
    def get_user_state(self,email:str) -> str|None:
        self.cursor.execute("select user_state from user where email=%s",(email))
        result=self.cursor.fetchone()
        if(result is not None):
            return result[0]
        else:
            return None
    
    def read_message(self,id:int|str) -> None:
        if(isinstance(id,int)):
            id=str(id)
        self.cursor.execute("update message set is_read=1 where id=%s",(id))
        self.db.commit()
    
    def get_history(self,email:str) -> tuple:
        self.cursor.execute("select * from history where email=%s order by conversation_time desc",(email))
        return self.cursor.fetchall()
    
    def insert_history(self,email:str,conversation_time:str,question:str,answer:str) -> None:
        self.cursor.execute("insert into history(email,conversation_time,question,answer) values (%s,%s,%s,%s)",
                            (email,conversation_time,question,answer))
        self.db.commit()
    
    def get_gender(self,email:str) -> str|None:
        self.cursor.execute("select gender from user where email=%s",(email))
        result=self.cursor.fetchone()
        if(result is not None):
            return result[0]
        else:
            return None
    
    def set_gender(self,email:str,gender:str) -> None:
        if gender in ['male','female']:
            self.cursor.execute("update user set gender=%s where email=%s",(gender,email))
        else:
            self.cursor.execute("update user set gender=NULL where email=%s",(email))
        self.db.commit()

    def get_age(self,email:str) -> int|None:
        self.cursor.execute("select age from user where email=%s",(email))
        result=self.cursor.fetchone()
        if(result is not None):
            return result[0]
        else:
            return None
    
    def set_age(self,email:str,age:int) -> None:
        if age is not None:
            self.cursor.execute("update user set age=%s where email=%s",(age,email))
        else:
            self.cursor.execute("update user set age=NULL where email=%s",(email))
        self.db.commit()

    def get_height(self,email:str) -> float|None:
        self.cursor.execute("select height from user where email=%s",(email))
        result=self.cursor.fetchone()
        if(result is not None):
            return result[0]
        else:
            return None

    def set_height(self,email:str,height:float) -> None:
        if height is not None:
            self.cursor.execute("update user set height=%s where email=%s",(height,email))
        else:
            self.cursor.execute("update user set height=NULL where email=%s",(email))
        self.db.commit()
    
    def get_weight(self,email:str) -> float|None:
        self.cursor.execute("select weight from user where email=%s",(email))
        result=self.cursor.fetchone()
        if(result is not None):
            return result[0]
        else:
            return None

    def set_weight(self,email:str,weight:float) -> None:
        if weight is not None:
            self.cursor.execute("update user set weight=%s where email=%s",(weight,email))
        else:
            self.cursor.execute("update user set weight=NULL where email=%s",(email,))
        self.db.commit()
    
    def get_fpg(self,email:str) -> float|None:
        self.cursor.execute("select fpg from user where email=%s",(email))
        result=self.cursor.fetchone()
        if(result is not None):
            return result[0]
        else:
            return None

    def set_fpg(self,email:str,fpg:float) -> None:
        if fpg is not None:
            self.cursor.execute("update user set fpg=%s where email=%s",(fpg,email))
        else:
            self.cursor.execute("update user set fpg=NULL where email=%s",(email,))
        self.db.commit()
    
    def get_ogtt(self,email:str) -> float|None:
        self.cursor.execute("select ogtt from user where email=%s",(email))
        result=self.cursor.fetchone()
        if(result is not None):
            return result[0]
        else:
            return None
    
    def set_ogtt(self,email:str,ogtt:float) -> None:
        if ogtt is not None:
            self.cursor.execute("update user set ogtt=%s where email=%s",(ogtt,email))
        else:
            self.cursor.execute("update user set ogtt=NULL where email=%s",(email,))
        self.db.commit()
    
    def get_hba1c(self,email:str) -> float|None:
        self.cursor.execute("select hba1c from user where email=%s",(email))
        result=self.cursor.fetchone()
        if(result is not None):
            return result[0]
        else:
            return None
    
    def set_hba1c(self,email:str,hba1c:float) -> None:
        if hba1c is not None:
            self.cursor.execute("update user set hba1c=%s where email=%s",(hba1c,email))
        else:
            self.cursor.execute("update user set hba1c=NULL where email=%s",(email,))
        self.db.commit()
    
    def update_body(self,email:str,body:dict) -> None:
        self.set_gender(email,body["gender"])
        self.set_age(email,body["age"])
        self.set_height(email,body["height"])
        self.set_weight(email,body["weight"])
        self.set_fpg(email,body["fpg"])
        self.set_ogtt(email,body["ogtt"])
        self.set_hba1c(email,body["hba1c"])

def get_database(database:list|Database) -> Database:
    if(isinstance(database,Database)):
        return database
    elif(isinstance(database,list)):
        index=random.randint(0,len(database)-1)
        return database[index]
    else:
        raise TypeError

if __name__ =='__main__':
    from functionsAndClasses import WebConfig
    import os
    web_config=WebConfig(os.getcwd()+'\\backend\\config\\web_config.cfg')
    db=Database(web_config.sql_host,web_config.sql_port,web_config.sql_user,web_config.sql_password,web_config.sql_db)
    print(db.check_user_state('2235060401@qq.com'))
    # for message in db.get_message_unread('zbx05@outlook.com'):
    #     print(message[0])
    # print(db.get_message('zbx04@outlook.com')==())
    # db.create_message('zbx04@outlook.com','zbx05@outlook','2024-1-18 15:01','用户忘记密码，请求重置密码。')
