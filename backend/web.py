import os
from langchain_community.chat_message_histories import ChatMessageHistory
from flask import Flask,render_template,request,redirect,url_for,session,Response,render_template_string
from flask_session import Session
import time
from py2neo import Graph
from sql import Database
from agent import *
from functionsAndClasses import *
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.dirname(os.path.abspath(__file__))+"/config/.env")

neo4j_browser_url_total = os.getenv("NEO4J_BROSWER_URL_TOTAL")
neo4j_browser_url = os.getenv("NEO4J_BROSWER_URL")

web_config=WebConfig(os.getcwd()+'\\config\\web_config.cfg')
gh=Graph(host=neo4j_browser_url,user=neo4j_username,password=neo4j_password)
db=Database(host=web_config.sql_host,port=web_config.sql_port,user=web_config.sql_user,password=web_config.sql_password,
                  target=web_config.sql_db)
# qa=Dialog(Graph(host=web_config.graph_host,user=web_config.graph_user,password=web_config.graph_password),web_config.dialog_too_long)
agent_executor=None
qa=run_agent_once
app=Flask(__name__,template_folder='../frontend',static_folder='../frontend/statics')
app.config.from_object(APPConfig)
Session(app)
print('App started.')
# print('https://'+web_config.app_host+':'+str(web_config.app_port))

@app.route('/login')
def login() -> str:
    return render_template('login.html')

@app.route('/register')
def register() -> str:
    return render_template('register.html')

@app.route('/forget')
def forget() -> str:
    return render_template('forget.html')

@app.route('/')
def default() -> Response:
    return redirect(url_for('login'),code=301)

@app.route('/account')
def account() -> str|Response:
    try:
        user=session["user"]
    except KeyError:
        return do_account_logout()
    if(user["type"]=="admin"):
        session["message"]=[]
        database=db
        message_tuple=database.get_message_unread(user["email"])
        if(message_tuple==()):
            message='''<div class="message-item">
                            <b>无消息</b>
                    </div>'''
        else:
            message=''''''
            idx=0
            for m in message_tuple:
                item=f'''<div class="message-item">
                        <p><b>时间：</b>{m[3]}</p>
                        <p><b>发送人邮箱：</b>{m[1]}</p>
                        <p><b>内容：</b>{m[4]}</p>
                        <p id="p-{idx}">
                            <button type="button" class="btn btn-success" id="btn-read-{idx}" onclick="read_message_request({idx})">
                                设为已读
                            </button>
                        </p>
                    </div>'''
                message+=item
                session["message"].append(m[0])
                idx+=1
        return render_template('accountAdmin.html',user_email=user["email"],
                               user_type='管理员用户' if user["type"]=='admin' else '普通用户',
                               user_state='封禁' if user["state"]=='ban' else '正常',
                               message=message)
    else:
        return render_template('accountUsr.html',user_email=user["email"],
                               user_type='管理员用户' if user["type"]=='admin' else '普通用户',
                               user_state='封禁' if user["state"]=='ban' else '正常')

@app.route('/dialog')
def dialog() -> str|Response:
    try:
        user=session["user"]
    except KeyError:
        return do_account_logout()
    return render_template('dialog.html') if user["state"]!='ban' else redirect(url_for('account'),code=302)

def neo4j() -> str|Response:
    try:
        session["user"]
    except KeyError:
        return do_account_logout()
    # return render_template_string(f'''
    #     <script>
    #         window.open('{web_config.graph_host}', '_blank');
    #     </script>
    #     ''')
    return render_template_string(f'''
        <script>
            window.open('https://www.baidu.com', '_blank');
        </script>
        ''')

@app.route('/graph')
def graph_() -> str|Response:
    try:
        user=session["user"]
    except KeyError:
        return do_account_logout()
    if user["type"]=='admin':
        return render_template('graphNeo4j.html',
                    neo4j_location=neo4j_browser_url_total)
    else:
        return render_template('graph.html')

@app.route('/history')
def history() -> str|Response:
    try:
        user=session["user"]
    except KeyError:
        return do_account_logout()

    if user["state"]=='ban':
        return redirect(url_for('account'),code=302)

    # 尝试从缓存读取历史记录
    try:
        history_data=session["history"]
    except KeyError:
        email=user["email"]
        database=db
        history_data=database.get_history(email)
        session["history"]=history_data

    # 改为结构化数据，交给前端 JS 做 markdown 渲染
    history_items=[]
    for history_tuple in history_data:
        history_items.append({
            "time": history_tuple[2],
            "question": history_tuple[3],
            "answer": history_tuple[4]
        })

    return render_template('history.html', history_items=history_items)

@app.route('/body')
def body() -> str|Response:
    try:
        user=session["user"]
    except KeyError:
        return do_account_logout()
    
    if user["state"]=='ban':
        return redirect(url_for('account'),code=302)
    
    gender=user["gender"] if user["gender"] is not None else ''
    age=user["age"] if user["age"] is not None else ''
    height=user["height"] if user["height"] is not None else ''
    weight=user["weight"] if user["weight"] is not None else ''
    fpg=user["fpg"] if user["fpg"] is not None else ''
    ogtt=user["ogtt"] if user["ogtt"] is not None else ''
    hba1c=user["hba1c"] if user["hba1c"] is not None else ''
    return render_template('body.html', user_gender=gender, user_age=age, user_height=height, 
                           user_weight=weight, user_fpg=fpg, user_ogtt=ogtt, user_hba1c=hba1c)

@app.route('/do/login',methods=['POST'])
def do_login() -> dict:
    session.clear()
    form=request.form.to_dict()
    email=form["email"]
    password=form["password"]
    database=db
    if(database.check_user_email(email) is None):
        return {"type":"info","id":"email","content":"邮箱错误。"}
    if(not database.check_user_password(email,password)):
        return {"type":"info","id":"password","content":"密码错误。"}
    user_data=database.get_user_data(email)
    session["user"]={"email":user_data[0],"type":user_data[2],"state":user_data[3],
                     "gender":user_data[4],"age":user_data[5],"height":user_data[6],
                     "weight":user_data[7],"fpg":user_data[8],"ogtt":user_data[9],"hba1c":user_data[10]}
    return {"type":"url","content":url_for('dialog') if user_data[3]!='ban' else url_for('account')}

@app.route('/do/register',methods=['POST'])
def do_register() -> dict:
    form=request.form.to_dict()
    check=register_check(form)
    if(check[0]==False):
        return {"type":"info","content":check[1]}
    email=check[1]
    password=check[2]
    database=db
    if(database.check_user_email(email) is None):
        database.create_user(email,password)
        return {"type":"url","content":url_for('default')}
    else:
        return {"type":"info","content":"邮箱已被注册。"}
    
@app.route('/do/forget',methods=['POST'])
def do_forget() -> dict:
    form=request.form.to_dict()
    email=form["email"]
    database=db
    if(database.check_user_email(email) is None):
        return {"type":"info","content":"邮箱错误。"}
    elif(database.get_user_state(email)=='ban'):
        return {"type":"info","content":"用户已被封禁。"}
    else:
        database.create_message(email,web_config.app_admin,time.strftime(r'%Y-%m-%d %H:%M:%S',time.localtime()),"用户忘记密码。")
        return {"type":"url","content":url_for('default')}

@app.route('/do/dialog',methods=['POST'])
def do_dialog() -> dict:
    try:
        user=session["user"]
    except KeyError:
        session.clear()
        return {"type":"url","content":url_for('default')}

    database=db
    form=request.form.to_dict()
    request_time=form["time"]
    question=form["question"]

    answer_text=None

    # 先尝试从会话缓存命中
    chat_history = ChatMessageHistory()
    try:
        records=session["dialog"]
        for record in records:
            chat_history.add_user_message(record.get("question"))
            chat_history.add_ai_message(record.get("answer_text"))
            if record.get("question")==question:
                # 兼容老缓存字段
                if "answer_text" in record:
                    answer_text=record["answer_text"]
                else:
                    answer_text=record.get("answer", "")
                time.sleep(3)
                break
    except KeyError:
        records=None

    # 缓存未命中则调用 qa
    if answer_text is None:
        qa_used=qa
        get_sql_tool = build_get_body_tool(database=db,email=user["email"])
        update_sql_tool = build_update_body_tool(database=db,email=user["email"],
                                                 session_data=session["user"])
        agent_executor=create_agent(
		    model=main_llm,
		    tools=[graph_tool, get_sql_tool, update_sql_tool],
		    system_prompt=AGENT_SYSTEM_PROMPT,
		    debug=True,
	    )
        answer_text=qa_used(agent_executor, question, user["email"], history=chat_history, 
                            debug=True if user["type"]=='admin' else False)

        if records is None:
            session["dialog"]=[{
                "time":request_time,
                "question":question,
                "answer_text":answer_text
            }]
        else:
            session["dialog"].append({
                "time":request_time,
                "question":question,
                "answer_text":answer_text
            })

    answer_for_history=str(answer_text)

    # 尝试向缓存写入历史记录
    try:
        session["history"]=tuple([(0,user["email"],request_time,question,answer_for_history)])+session["history"]
    except KeyError:
        history_data=database.get_history(user["email"])
        session["history"]=tuple([(0,user["email"],request_time,question,answer_for_history)])+history_data

    database.insert_history(user["email"],request_time,question,answer_for_history)
    agent_executor=None
    get_sql_tool=None
    update_sql_tool=None

    return {"type":"answer","content":answer_text}

@app.route('/do/account/change',methods=['POST'])
def do_account_change() -> dict:
    try:
        user=session["user"]
    except KeyError:
        session.clear()
        return {"type":"error","content":url_for('default')}
    form=request.form.to_dict()
    database=db
    if(user["type"]=='usr'):
        password=form["password"]
        password_again=form["password_again"]
        result,info=check_password_format(password,password_again)
        if(not result):
            return {"type":"info","content":info}
        database.set_user_password(user["email"],password)
        session.clear()
        return {"type":"url","content":url_for('default')}
    elif(user["type"]=='admin'):
        email=form["email"]
        password=form["password"]
        password_again=form["password_again"]
        result,info=check_password_format(password,password_again)
        if(not result):
            return {"type":"info","content":info}
        database.set_user_password(email,password)
        if(email==user["email"]):
            session.clear()
            return {"type":"url","content":url_for('default')}
        else:
            return {"type":"info","content":"修改成功，请及时通知用户。"}

@app.route('/do/account/logout',methods=['POST'])
def do_account_logout() -> Response:
    session.clear()
    return redirect(url_for('default'),code=302)

@app.route('/do/account/create',methods=['POST'])
def do_account_create() -> dict:
    form=request.form.to_dict()
    check=register_check(form)
    if(check[0]==False):
        return {"type":"info","content":check[1]}
    email=check[1]
    password=check[2]
    database=db
    if(database.check_user_email(email) is None):
        database.create_user(email,password)
        return {"type":"info","content":"创建用户成功。"}
    else:
        return {"type":"info","content":"邮箱已被注册。"}

@app.route('/do/account/ban',methods=['POST'])
def do_account_ban() -> dict:
    try:
        user=session["user"]
    except KeyError:
        session.clear()
        return {"type":"url","content":url_for('default')}
    form=request.form.to_dict()
    action_type=form["type"]
    email=form["email"]
    database=db
    if(action_type=='ban'):
        if(email==user["email"]):
            return {"type":"info","id":"email-2","content":"您正在尝试封禁自己。"}
        if(database.check_user_email(email) is None):
            return {"type":"info","id":"email-2","content":"未找到用户。"}
        _,_,user_type,user_current_state=database.get_user_data(email)
        if(user_current_state=='ban'):
            return {"type":"info","id":"email-2","content":"该用户已处于封禁状态。"}
        if(user_type=='admin'):
            return {"type":"info","id":"email-2","content":"该用户为管理员。"}
        database.set_user_state(email,'ban')
        return {"type":"info","id":"alert","content":"封禁成功。"}
    elif(action_type=='unban'):
        if(database.check_user_email(email) is None):
            return {"type":"info","id":"email-2","content":"未找到用户。"}
        _,_,user_type,user_current_state=database.get_user_data(email)
        if(user_current_state=='active'):
            return {"type":"info","id":"email-2","content":"该用户未被封禁。"}
        database.set_user_state(email,'active')
        return {"type":"info","id":"alert","content":"解封成功。"}
    
@app.route('/do/account/message',methods=['POST'])
def do_account_message() -> dict:
    try:
        session["message"]
    except KeyError:
        session.clear()
        return {"type":"url","content":url_for('default')}
    form=request.form.to_dict()
    idx=eval(form["idx"])
    database=db
    database.read_message(session["message"][idx])
    return {"type":"info","content":"success"}

@app.route('/do/graph',methods=['POST'])
def do_graph() -> dict:
    try:
        session["user"]
    except KeyError:
        session.clear()
        return {"type":"url","content":url_for('default')}
    graph=gh
    form=request.form.to_dict()
    name=form["name"]
    if(name==''):
        try:
            return {"type":"data","content":session["graph"]}
        except KeyError:
            graph_data=graph.run('match (m)-[r]->(n) return id(m),labels(m),m.name,r.name,id(n),labels(n),n.name order by rand() limit 1000').data()
            session["graph"]=read_graph_data(graph_data)
            return {"type":"data","content":session["graph"]}
    else:
        graph_data=graph.run('match (m)-[r]->(n) where n.name=$name return id(m),labels(m),m.name,r.name,id(n),labels(n),n.name limit 1000'
                             ,{"name":name}).data()
        if(len(graph_data)==0):
            graph_data=graph.run('match (n) where n.name=$name return id(n),labels(n),n.name limit 1000'
                             ,{"name":name}).data()
            return {"type":"data","content":read_single_graph_data(graph_data)}
        return {"type":"data","content":read_graph_data(graph_data)}

@app.route('/do/body/change',methods=['POST'])
def do_body_change() -> dict:
    try:
        user=session["user"]
    except KeyError:
        session.clear()
        return {"type":"url","content":url_for('default')}
    form=request.form.to_dict()
    body={
        "gender": form["gender"] if form["gender"] != '' else None,
        "age": int(form["age"]) if form["age"] != '' else None,
        "height": float(form["height"]) if form["height"] != '' else None,
        "weight": float(form["weight"]) if form["weight"] != '' else None,
        "fpg": float(form["fpg"]) if form["fpg"] != '' else None,
        "ogtt": float(form["ogtt"]) if form["ogtt"] != '' else None,
        "hba1c": float(form["hba1c"]) if form["hba1c"] != '' else None
    }
    for key in body.keys():
        session["user"][key]=body[key]
    database=db
    database.update_body(user["email"],body)
    return {"type":"info","content":"更新成功。"}
