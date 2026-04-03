import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from langchain_neo4j import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage

import json
import time
import re
import asyncio

os.environ["SPORTS_DATA_DIR"] = os.getcwd()+"/data/spiderData/sport.json"
os.environ["LANGSMITH_TRACING"] = "false"

load_dotenv("./.env")
# model = os.getenv("VLLM_MODEL")
# base_url = os.getenv("VLLM_BASE_URL")
# api_key = os.getenv("VLLM_API_KEY")
llm = ChatOpenAI(model="gpt-4o")

neo4j_url = os.getenv("NEO4J_URL")
neo4j_username = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")
neo4j_database = os.getenv("NEO4J_DATABASE")

try:
    graph = Neo4jGraph(
        url=neo4j_url,
        username=neo4j_username,
        password=neo4j_password,
        database=neo4j_database,
        refresh_schema=False
    )
    graph.query("RETURN 1 as ok")
except Exception as e:
    print("Neo4j 连接失败: ", e)
    exit()

with open(os.getenv("SPORTS_DATA_DIR"),"r",encoding="utf-8",errors="ignore") as fp:
    sports_data=json.load(fp)
sports_data_contents=sports_data.get("contents", [])
total_num=len(sports_data_contents)


def _is_rate_limit_error(error: Exception) -> bool:
    message = str(error).lower()
    keywords = [
        "rate_limit_exceeded",
        "rate limit reached",
        "tokens per min",
        "please try again in",
        "429",
    ]
    return any(keyword in message for keyword in keywords)


def _extract_retry_seconds(error: Exception, attempt: int) -> float:
    """识别错误信息中的重试时间，并尝试等待指定的时间后重试。"""
    message = str(error)

    ms_match = re.search(r"please try again in\s*(\d+)\s*ms", message, re.IGNORECASE)
    if ms_match:
        return min(max(float(ms_match.group(1)) / 1000.0 + 0.05, 0.2), 10.0)

    sec_match = re.search(r"please try again in\s*([0-9]*\.?[0-9]+)\s*s", message, re.IGNORECASE)
    if sec_match:
        return min(max(float(sec_match.group(1)) + 0.05, 0.2), 10.0)
    return min(0.5 * (2 ** attempt), 10.0)


async def _adaptive_sleep_for_rate_limit(error: Exception, attempt: int, scope: str) -> bool:
    if not _is_rate_limit_error(error):
        return False
    sleep_seconds = _extract_retry_seconds(error, attempt)
    print(f"{scope} 命中限流，等待 {sleep_seconds:.2f}s 后重试...")
    await asyncio.sleep(sleep_seconds)
    return True

async def align_disease_with_llm(extracted_diseases: set, existing_diseases: list) -> dict:
    """
    使用 LLM 对抽取的 Disease 名称与数据库中已有的 Disease 进行语义对齐。
    返回映射字典：{抽取的disease名称 -> 对齐后的disease名称或[New]}，其中 [New] 表示该疾病在数据库中没有匹配项，需要新建节点。
    """
    if not extracted_diseases:
        return {}
    
    existing_diseases_str = "\n".join([f"- {d}" for d in existing_diseases])
    extracted_diseases_str = "\n".join(sorted(list(extracted_diseases)))
    
    alignment_prompt = f"""你是一位医学领域的专家。需要将以下抽取的疾病名称与已存在于数据库中的疾病名称进行语义对齐。
已存在的疾病列表：
{existing_diseases_str}

需要对齐的疾病名称：
{extracted_diseases_str}

请对每个需要对齐的疾病，找到最匹配的已存在疾病，如果没有相关的已存在疾病，则输出 "[New]"

返回格式为 JSON，如下所示：
{{
  "抽取的疾病名称1": "已存在的疾病名称1",
  "抽取的疾病名称2": "[New]",
  ...
}}

只返回 JSON 对象，无其他文本。"""
    
    for attempt in range(5):
        try:
            message = HumanMessage(content=alignment_prompt)
            response = await asyncio.to_thread(llm.invoke, [message])
            response_text = response.content.strip()

            try:
                alignment_dict = json.loads(response_text)
                print(f"\nLLM 对齐结果：")
                for extracted, aligned in alignment_dict.items():
                    if aligned == "[New]":
                        print(f"  {extracted} -> [New]")
                    else:
                        print(f"  {extracted} -> {aligned}")
                return alignment_dict
            except json.JSONDecodeError:
                json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
                if json_match:
                    alignment_dict = json.loads(json_match.group())
                    print(f"\nLLM 对齐结果（从文本中提取）：")
                    for extracted, aligned in alignment_dict.items():
                        if aligned == "[New]":
                            print(f"  {extracted} -> [New]")
                        else:
                            print(f"  {extracted} -> {aligned}")
                    return alignment_dict
                
                print(f"\nLLM 响应格式错误，无法解析：{response_text}")
                return {disease: "[New]" for disease in extracted_diseases}
        except Exception as e:
            should_retry = await _adaptive_sleep_for_rate_limit(e, attempt, "Disease 对齐")
            if not should_retry:
                print(f"\nLLM 对齐失败: {e}")
                return {disease: "[New]" for disease in extracted_diseases}

    print("\nLLM 对齐重试次数耗尽，回退为 [New]。")
    return {disease: "[New]" for disease in extracted_diseases}

async def main():
    if total_num == 0:
        print("未读取到任何运动数据。")
        return

    documents = []
    for index, item in enumerate(sports_data_contents, start=1):
        title = item.get("title", "").strip()
        summary = item.get("summary", "").strip()
        content = item.get("content", "").strip()
        if not any([title, summary, content]):
            continue

        text = f"摘要：{summary}\n内容：{content}"
        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": "sport.json",
                    "index": index,
                    "title": title,
                },
            )
        )

    if not documents:
        print("运动数据存在，但没有可用于抽取的有效文本。")
        return

    # llm_prompt = ChatPromptTemplate.from_messages(
    #     [
    #         (
    #             "system",
    #             "你是一位经验丰富的运动医学专家。请从文本中抽取运动相关知识图谱，节点类型为 Sport 和 Disease，关系类型为 Sport_Suitable_Disease，关系方向为 Sport -> Disease。仅输出结构化抽取结果，不要添加解释。",
    #         ),
    #         ("human", "请从以下文本中抽取：\n{input}"),
    #     ]
    # )
    llm_transformer = LLMGraphTransformer(llm=llm,
                                          allowed_nodes=["Sport", "Disease"],
                                          node_properties=True,
                                          allowed_relationships=["Sport_Suitable_Disease"],
                                          relationship_properties=True,
                                        #   prompt=llm_prompt,
                                          additional_instructions="关系方向为 Sport -> Disease，类型为 Sport_Suitable_Disease。抽取Sport时实体时，如果实体名称为英文，请将其翻译成中文。",
                                        )
    batch_size = 5
    graph_documents = []

    for start in range(0, len(documents), batch_size):
        end = min(start + batch_size, len(documents))
        batch_documents = documents[start:end]
        batch_ok = False
        for attempt in range(3):
            try:
                batch_graph_documents = await llm_transformer.aconvert_to_graph_documents(batch_documents)
                graph_documents.extend(batch_graph_documents)
                print(f"已完成图谱抽取: {end}/{len(documents)}")
                batch_ok = True
                break
            except Exception as e:
                should_retry = await _adaptive_sleep_for_rate_limit(e, attempt, f"批次 {start + 1}-{end}")
                if not should_retry:
                    print(f"批次 {start + 1}-{end} 抽取失败，降级为逐条抽取。错误: {e}")
                    break

        if batch_ok:
            continue

        for document in batch_documents:
            single_ok = False
            for single_attempt in range(3):
                try:
                    single_graph_documents = await llm_transformer.aconvert_to_graph_documents([document])
                    graph_documents.extend(single_graph_documents)
                    single_ok = True
                    break
                except Exception as single_error:
                    should_retry = await _adaptive_sleep_for_rate_limit(
                        single_error,
                        single_attempt,
                        f"文档 {document.metadata.get("title", "")}"
                    )
                    if not should_retry:
                        break
            if not single_ok:
                title = document.metadata.get("title", "")
                print(f"跳过异常文档: {title}.")

        print(f"已完成图谱抽取: {end}/{len(documents)}")

    valid_graph_documents = [
        graph_document
        for graph_document in graph_documents
        if graph_document.nodes or graph_document.relationships
    ]

    if not valid_graph_documents:
        print("LLM 未抽取到任何节点或关系，未写入 Neo4j。")
        return

    node_count = sum(len(graph_document.nodes) for graph_document in valid_graph_documents)
    relationship_count = sum(len(graph_document.relationships) for graph_document in valid_graph_documents)
    print(f"共抽取节点 {node_count} 个，关系 {relationship_count} 条。")
    print(f"示例节点: {valid_graph_documents[0].nodes}")
    print(f"示例关系: {valid_graph_documents[0].relationships}")

    # 处理 Disease 节点：先查询数据库中所有已有的 Disease
    print("\n从数据库查询已有的 Disease 节点...")
    existing_db_diseases = graph.query(
        "MATCH (d:Disease) RETURN d.name AS name"
    )
    existing_db_disease_names = [record["name"] for record in existing_db_diseases if record["name"]]
    print(f"数据库中已有 {len(existing_db_disease_names)} 个 Disease 节点")
    
    # 收集所有抽取的 Disease 节点名称
    all_disease_names = set()
    for graph_doc in valid_graph_documents:
        for node in graph_doc.nodes:
            if node.type and "disease" in node.type.lower():
                all_disease_names.add(node.id)
    
    print(f"LLM 抽取了 {len(all_disease_names)} 个 Disease 节点\n")

    if all_disease_names:
        # 使用 LLM 进行语义对齐
        print("使用 LLM 进行 Disease 语义对齐...")
        alignment_dict = await align_disease_with_llm(all_disease_names, existing_db_disease_names)
        
        # 基于对齐结果更新 graph_documents 中的 Disease 节点和关系
        print("\n更新 graph_documents 中的 Disease 引用...")
        for graph_doc in valid_graph_documents:
            # 更新节点中的 Disease 名称
            for node in graph_doc.nodes:
                if node.type and "disease" in node.type.lower():
                    if node.id in alignment_dict:
                        aligned_name = alignment_dict[node.id]
                        if aligned_name != "[New]":
                            node.id = aligned_name
                            print(f"  节点对齐: {node.id} <- {node.id}")
            
            # 更新关系中的 Disease 引用
            for rel in graph_doc.relationships:
                if rel.type and "suitable" in rel.type.lower():
                    # Relationship 使用 source/target 节点对象，而非 source_id/target_id
                    target_node = rel.target
                    if (
                        target_node
                        and target_node.type
                        and "disease" in target_node.type.lower()
                        and target_node.id in alignment_dict
                    ):
                        aligned_name = alignment_dict[target_node.id]
                        if aligned_name != "[New]":
                            original_target = target_node.id
                            target_node.id = aligned_name
                            source_name = rel.source.id if rel.source else ""
                            print(f"  关系对齐: {source_name} -[{rel.type}]-> {original_target} -> {aligned_name}")
        
        # 确定需要创建的 Disease 节点
        diseases_to_create = set()
        for disease_name, aligned_name in alignment_dict.items():
            if aligned_name == "[New]":
                diseases_to_create.add(disease_name)
        
        # # 创建缺失的 Disease 节点
        # if diseases_to_create:
        #     print(f"\n创建缺失的 Disease 节点，共 {len(diseases_to_create)} 个...")
        #     for disease_name in diseases_to_create:
        #         try:
        #             graph.query(
        #                 "CREATE (d:Disease{name:$name})",
        #                 {"name": disease_name}
        #             )
        #             print(f"已创建新 Disease 节点: {disease_name}")
        #         except Exception as e:
        #             print(f"创建 Disease 节点失败 {disease_name}: {e}")
        
        aligned_count = len([v for v in alignment_dict.values() if v != "[New]"])
        # with open(os.getcwd()+"/txt/disease.txt","w+",encoding="utf-8") as fp:
        #     fp.write("\n".join(list(diseases_to_create)))
        print(f"\nDisease 处理完毕：对齐到已有节点 {aligned_count} 个，新建 {len(diseases_to_create)} 个。")

    extracted_data={ "entity": {"disease": list(diseases_to_create),"sport": []}, "relation": {"Sport_Suitable_Disease": []} }

    # 从 valid_graph_documents 读取 SPORT_SUITABLE_DISEASE 关系，存储在列表中
    # 格式为：[[source.id, target.id], ...]
    sport_suitable_disease_relations = []
    relation_seen = set()
    sport_entities = set()
    for graph_doc in valid_graph_documents:
        for rel in graph_doc.relationships:
            if not rel.type or rel.type.upper() != "SPORT_SUITABLE_DISEASE":
                continue
            if not rel.source or not rel.target:
                continue
            source_id = rel.source.id
            sport_entities.add(source_id)
            target_id = rel.target.id
            relation_key = (source_id, target_id)
            if relation_key in relation_seen:
                continue
            relation_seen.add(relation_key)
            sport_suitable_disease_relations.append([source_id, target_id])
    
    extracted_data["entity"]["sport"] = list(sport_entities)
    extracted_data["relation"]["Sport_Suitable_Disease"] = sport_suitable_disease_relations

    with open(os.getcwd()+"/data/extractedData/extracted_sport.json", "w", encoding="utf-8", errors="ignore") as fp:
        json.dump(extracted_data, fp, ensure_ascii=False)
    # print(f"\n将 Sport 节点及对齐后的关系写入 Neo4j...")
    # graph.add_graph_documents(
    #     valid_graph_documents,
    #     baseEntityLabel=True,
    #     include_source=True,
    # )

    # sports = set()
    # for graph_doc in valid_graph_documents:
    #     for node in graph_doc.nodes:
    #         if node.type and "sport" in node.type.lower():
    #             sports.add(node.id)
    # with open(os.getcwd()+"/txt/sport.txt", "w+", encoding="utf-8") as fp:
    #     fp.write("\n".join(sorted(list(sports))))

    # print(f"\n已写入 Neo4j，共处理 {len(valid_graph_documents)} 篇文档。")
    print(f"\n已处理 {len(valid_graph_documents)} 篇文档。")
if __name__ == "__main__":
    asyncio.run(main())