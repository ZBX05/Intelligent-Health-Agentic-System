from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

response = client.chat.completions.create(
    model="M2-her",
    messages=[
        {
            "role": "system",
            "name": "AI助手",
            "content": "你是一个友好、专业的AI助手"
        },
        {
            "role": "user",
            "name": "用户",
            "content": "你好，请介绍一下你自己"
        }
    ],
    temperature=1.0,
    top_p=0.95,
    max_completion_tokens=2048
)

print(response.choices[0].message.content)

# response = client.chat.completions.create(
#     # model="MiniMax-M2.5",
#     model="M2-her",
#     messages=[
#         {"role": "system", "content": "你是一位经验丰富的医生，擅长诊断和治疗各种疾病。"},
#         {"role": "user_system", "content": "你是一位患者，出现了不适症状，你推测自己可能患有糖尿病。"},
#         # {"role": "user", "content": "医生您好，请问糖尿病的分型和典型症状都有哪些？"},
#         {"role": "user", "content": "医生您好，请问糖尿病的分型和典型症状都有哪些？"}
#     ],
#     # 设置 reasoning_split=True 将思考内容分离到 reasoning_details 字段
#     # extra_body={"reasoning_split": True},
#     temperature=1.0,
#     top_p=0.95,
#     max_completion_tokens=2048
# )

# print(f"Thinking:\n{response.choices[0].message.reasoning_details[0]['text']}\n")
# print(f"Text:\n{response.choices[0].message.content}\n")
# print(response)
# print(response.choices[0].message)