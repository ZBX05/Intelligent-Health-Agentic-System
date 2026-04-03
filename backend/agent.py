import asyncio
import os
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI
from tools import build_retrieve_graph_tool, build_update_body_tool, build_get_body_tool

load_dotenv(dotenv_path=os.path.dirname(os.path.abspath(__file__))+"/config/.env")

neo4j_url = os.getenv("NEO4J_URL")
neo4j_username = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")
neo4j_database = os.getenv("NEO4J_DATABASE")

chat_api_key = os.getenv("CHAT_API_KEY")
chat_base_url = os.getenv("CHAT_BASE_URL")
chat_model = os.getenv("CHAT_MODEL")

graph_api_key = os.getenv("GRAPH_API_KEY")
graph_base_url = os.getenv("GRAPH_BASE_URL")
graph_model = os.getenv("GRAPH_MODEL")

def get_session_history(session_id: str, history: dict = None) -> ChatMessageHistory:
	"""根据 session_id 获取会话历史，不存在则创建。"""
	if session_id not in history:
		history[session_id] = ChatMessageHistory()
	return history[session_id]

main_llm = ChatOpenAI(
	model=chat_model,
	openai_api_key=chat_api_key,
	openai_api_base=chat_base_url,
	temperature=0,
)

graph_llm = ChatOpenAI(
	model=graph_model,
	openai_api_key=graph_api_key,
	openai_api_base=graph_base_url,
	extra_body={"reasoning_split": True}
)

try:
	graph = Neo4jGraph(
		url=neo4j_url,
		username=neo4j_username,
		password=neo4j_password,
		database=neo4j_database,
		timeout=60,
	)
	graph.refresh_schema()
except Exception as e:
	print(f"Neo4j 连接失败: {e}")
	graph = None


cypher_generation_template = """
任务：
为 Neo4j 图数据库生成 Cypher 查询。

要求：
1. 仅使用给定 schema 中出现的节点、关系和属性。
2. 仅生成只读查询，不得包含 CREATE / MERGE / DELETE / SET / REMOVE / DROP / CALL dbms / apoc.periodic 等写操作或管理操作。
3. 回答必须只有一条可执行 Cypher，不要输出任何解释、前后缀、Markdown 代码块。
4. 保证关系方向和别名正确。
5. 如果涉及计算，注意避免除零。

模式:
{schema}

用户问题:
{question}
"""

cypher_prompt = PromptTemplate(
	input_variables=["schema", "question"],
	template=cypher_generation_template,
)

cypher_forbidden_keywords = [
	" create ",
	" merge ",
	" delete ",
	" detach ",
	" set ",
	" remove ",
	" drop ",
	" load csv",
	" call dbms",
	" apoc.periodic"
]

AGENT_SYSTEM_PROMPT = """ 您是一个医疗助手，主攻糖尿病及其并发症的诊断和治疗。
您拥有丰富的临床经验数据，能够根据患者的症状、体征、实验室检查结果和影像学资料，准确地诊断糖尿病及其相关疾病，
并制定个性化的治疗方案。您有一个存储了糖尿病知识的图数据库，可根据Neo4j Cypher查询的结果生成人类可读的响应。

已有工具：
1. graph_tool：根据用户问题从图数据库中检索相关知识，返回结构化数据 rows；
2. get_sql_tool：根据用户邮箱获取用户身体信息的字典；
3. update_sql_tool：根据用户邮箱更新用户身体信息的字典。

工作规则：
1. 当用户陈述或要求你帮助修改自己的身体信息（如年龄、性别、身高、体重、血糖等）时，解析用户给出的信息指标，调用 update_sql_tool 工具更新数据库中的身体信息；
2. 当用户询问与糖尿病相关的知识（如症状、检查、治疗等）时，优先调用 graph_tool 工具从图数据库中检索相关知识，然后调用 get_sql_tool 工具获取用户的身体信息和生理指标，辅助进行判断；
3. 工具返回 rows 时，应优先依据 rows 回答，并可结合常识补充解释；
4. 如果 rows 为空，可基于医学常识回答，但必须明确说明图谱未命中；
5. 回答要专业、谨慎、清晰，避免绝对化承诺，必要时建议线下就医。
6. 不要引导用户按步骤提供信息，请直接从用户的陈述或问题中提取信息并、适时调用工具并做出合适的回答。
""".strip()

graph_tool = build_retrieve_graph_tool(
    graph_llm=graph_llm,
    cypher_prompt=cypher_prompt,
    graph=graph,
    forbidden_keywords=cypher_forbidden_keywords
)

def _extract_text_from_agent_result(result: Any) -> str:
	"""
	从 agent_executor.invoke 的结果中提取最终文本响应。
	"""
	# 字典里有 messages
	if isinstance(result, dict):
		messages = result.get("messages")
		if isinstance(messages, list) and messages:
			# 逆序查找最后一个 AIMessage
			for msg in reversed(messages):
				if isinstance(msg, AIMessage):
					return str(msg.content)
			# 没有 AIMessage 时取最后一个消息内容
			last_msg = messages[-1]
			content = getattr(last_msg, "content", "")
			if content:
				return str(content)

		output = result.get("output")
		if output:
			return str(output)

	# 直接返回消息对象
	if isinstance(result, BaseMessage):
		return str(result.content)

	# 直接返回文本
	return str(result)


def run_agent_once(agent_executor: Any, question: str, email: str, history: dict = None, 
				   debug: bool = False) -> tuple[str, dict]:
	"""
	运行一次智能体，处理用户问题并返回答案。
	"""
	# history = get_session_history(session_id, history)

	input_messages = list(history.messages)
	input_messages.append(HumanMessage(content=question))

	result = agent_executor.invoke({"messages": input_messages},context={"email": email})
	final_answer = _extract_text_from_agent_result(result)

	history.add_user_message(question)
	history.add_ai_message(final_answer)

	return result if debug else final_answer 


async def chat_with_timeout(message: str, history: list) -> str:
	try:
		response = await asyncio.wait_for(
			asyncio.to_thread(run_agent_once, message, history),
			timeout=120.0,
		)
		return response
	except asyncio.TimeoutError:
		return "抱歉，本次请求处理超时。请尝试缩短问题或稍后重试。"
	except Exception as e:
		print(f"[AgentAuto] 处理异常：{e}")
		return "抱歉，系统暂时出现异常，请稍后重试。"


# if __name__ == "__main__":
# 	store: dict[str, ChatMessageHistory] = {}
# 	agent_executor=create_agent(
# 		model=main_llm,
# 		tools=[graph_tool],
# 		system_prompt=AGENT_SYSTEM_PROMPT,
# 		debug=False,
# 	)
# 	print(run_agent_once(agent_executor, "糖尿病适合什么运动？", history=store))
# 	# print(run_agent_once("2型糖尿病适合什么药物？",history=store))
# 	# print(store)
