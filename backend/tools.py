from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage
import json
from typing import Any, Callable
import re
from sql import Database

def _get_graph_schema(graph: Neo4jGraph) -> str:
	"""安全获取当前图谱 schema。"""
	if not graph:
		return ""

	try:
		schema = getattr(graph, "schema", "")
		if schema:
			return schema

		get_schema = getattr(graph, "get_schema", None)
		if callable(get_schema):
			return str(get_schema())
	except Exception as e:
		print(f"Neo4j 获取 schema 失败: {e}")

	return ""


def _sanitize_cypher(raw_text: str) -> str:
	"""去掉 ```cypher 包裹，保留可执行 Cypher。"""
	text = raw_text.strip()
	text = re.sub(r"^```(?:cypher)?\\s*", "", text, flags=re.IGNORECASE)
	text = re.sub(r"\\s*```$", "", text)
	return text.strip()


def _is_read_only_cypher(cypher: str, forbidden_keywords: list[str]) -> bool:
	"""
	粗粒度只读校验。
	防止模型误生成写入类语句，避免污染线上图谱数据。
	Args:
        cypher: The Cypher query to check.
        forbidden_keywords: A list of forbidden keywords.

    Returns:
        True: read-only cypher;
		False: otherwise.
	"""
	lowered = cypher.lower()
	padded = f" {lowered} "
	return not any(keyword in padded for keyword in forbidden_keywords)


def _run_graph_retrieval(question: str, graph_llm: ChatOpenAI, cypher_prompt: PromptTemplate, graph: Neo4jGraph,
						 forbidden_keywords: list[str]) -> dict[str, Any]:
	"""
	图谱检索核心逻辑：
	1) 使用 graph_llm 生成 Cypher
	2) 做安全检查
	3) 执行查询并返回结构化结果
	"""
	if not graph:
		return {
			"status": "error",
			"cypher": "",
			"rows": [],
			"message": "Neo4j 未连接，无法进行图谱检索。",
		}

	schema_text = _get_graph_schema(graph)
	if not schema_text:
		return {
			"status": "error",
			"cypher": "",
			"rows": [],
			"message": "未获取到图谱 schema，无法安全生成 Cypher。",
		}

	try:
		cypher_raw = (cypher_prompt | graph_llm).invoke(
			{"schema": schema_text, "question": question}
		)

		if isinstance(cypher_raw, AIMessage):
			cypher_text = str(cypher_raw.content)
		else:
			cypher_text = str(cypher_raw)

		cypher = _sanitize_cypher(cypher_text)
		if not cypher:
			return {
				"status": "error",
				"cypher": "",
				"rows": [],
				"message": "图谱模型未生成有效 Cypher。",
			}

		if not _is_read_only_cypher(cypher, forbidden_keywords):
			return {
				"status": "error",
				"cypher": cypher,
				"rows": [],
				"message": "生成的 Cypher 非只读语句，已拒绝执行。",
			}

		rows = graph.query(cypher)
		max_rows = 30
		clipped_rows = rows[:max_rows] if isinstance(rows, list) else []

		return {
			"status": "success",
			"cypher": cypher,
			"rows": clipped_rows,
			"message": "ok" if rows else "查询成功但结果为空。",
		}
	except Exception as e:
		return {
			"status": "error",
			"cypher": "",
			"rows": [],
			"message": f"图谱检索异常：{e}",
		}

def build_retrieve_graph_tool(graph_llm: ChatOpenAI, cypher_prompt: PromptTemplate, graph: Neo4jGraph, 
							  forbidden_keywords: list[str]) -> Callable[[str], str]:
	"""
	构建一个知识图谱查询工具。
	Args:
		graph_llm: 用于生成 Cypher 查询的语言模型。
        cypher_prompt: 生成 Cypher 查询的提示。
        graph: Neo4jGraph 实例。
        forbidden_keywords: 禁用关键词列表。
	Returns:
		retrieve_graph_knowledge: 一个工具函数，它接受一个问题字符串并返回一个包含查询结果的JSON字符串。
	"""

	@tool
	def retrieve_graph_knowledge(question: str) -> str:
		"""
		从知识图谱中检索与问题相关的证据，返回 JSON 字符串。
		Args:
        	question: 需要检索的问题问题。
		Other Args:
        	graph_llm: 用于生成 Cypher 查询的语言模型。
        	cypher_prompt: 生成 Cypher 查询的提示。
        	graph: Neo4jGraph 实例。
        	forbidden_keywords: 禁用关键词列表。

    	Returns:
        	一个 JSON 字符串，包含查询状态、生成的 Cypher 查询、查询结果和消息。
		"""
		result = _run_graph_retrieval(question, graph_llm, cypher_prompt, graph, forbidden_keywords)
		return json.dumps(result, ensure_ascii=False)

	return retrieve_graph_knowledge

def _update_body_by_dict(database: Database, email: str, update_dict: dict[str, int|float|str]) -> None:
	for key, value in update_dict.items():
		if key == "gender":
			database.set_gender(email, value)
		elif key == "age":
			database.set_age(email, value)
		elif key == "height":
			database.set_height(email, value)
		elif key == "weight":
			database.set_weight(email, value)
		elif key == "fpg":
			database.set_fpg(email, value)
		elif key == "ogtt":
			database.set_ogtt(email, value)
		elif key == "hba1c":
			database.set_hba1c(email, value)

def build_update_body_tool(database: Database, email: str, session_data: dict) -> Callable[[str, dict[str, int|float|str]], None]:
	@tool
	def update_body(update_dict: dict[str, int|float|str]) -> None:
		"""
		根据问题内容更新用户身体信息。
		Args:
			email: 用户邮箱。
			update_dict: 包含要更新的身体信息的字典，需要模型从用户输入的question中提取，格式说明：
			{
				"gender": [性别：'male' 或 'female'], 
				"age": [年龄：单位为岁，大于0的整数], 
				"height": [身高：单位为厘米，大于0的浮点数], 
				"weight": [体重：单位为千克，大于0的浮点数], 
				"fpg": [空腹血糖：单位为mmol/L，大于0的浮点数], 
				"ogtt": [OGTT：单位为mmol/L，大于0的浮点数], 
				"hba1c": [HbA1c：单位为%，大于0且小于等于100的浮点数]
			}
		"""
		for key, value in update_dict.items():
			if key == "gender":
				if "男" in value:
					update_dict["gender"] = "male"
				elif "女" in value:
					update_dict["gender"] = "female"
			elif key == "age":
				if value <= 0:
					update_dict["age"] = None
				session_data["age"] = update_dict["age"]
			elif key == "height":
				if value <= 0:
					update_dict["height"] = None
			elif key == "weight":
				if value <= 0:
					update_dict["weight"] = None
			elif key == "fpg":
				if value <= 0:
					update_dict["fpg"] = None
			elif key == "ogtt":
				if value <= 0:
					update_dict["ogtt"] = None
			elif key == "hba1c":
				if value <= 0 or value > 100:
					update_dict["hba1c"] = None
			session_data[key] = update_dict[key]
		return _update_body_by_dict(database, email, update_dict)
	return update_body

def _get_body_dict_by_email(database: Database, email: str) -> dict[str, int|float|str]:
		result = {
			"gender":database.get_gender(email),
			"age":int(database.get_age(email)),
			"height":float(database.get_height(email)),
			"weight":float(database.get_weight(email)),
			"fpg":float(database.get_fpg(email)),
			"ogtt":float(database.get_ogtt(email)),
			"hba1c":float(database.get_hba1c(email))
		}
		return result

def build_get_body_tool(database: Database, email: str) -> Callable[[str], dict[str, int|float|str]]:
	@tool
	def get_body_dict() -> dict[str, int|float|str]:
		"""
		根据用户邮箱获取用户身体信息。
		Returns:
			包含用户身体信息的字典，字典格式：
			{
				"gender": [性别：'male' 或 'female'], 
				"age": [年龄：单位为岁，大于0的整数], 
				"height": [身高：单位为厘米，大于0的浮点数], 
				"weight": [体重：单位为千克，大于0的浮点数], 
				"fpg": [空腹血糖：单位为mmol/L，大于0的浮点数], 
				"ogtt": [OGTT：单位为mmol/L，大于0的浮点数], 
				"hba1c": [HbA1c：单位为%，大于0且小于等于100的浮点数]
			}
		"""
		return _get_body_dict_by_email(database, email)
	return get_body_dict
