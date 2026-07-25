from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=BASE_URL
)

# response = client.chat.completions.create(
#             model=OPENAI_MODEL_NAME,
#             messages=[
#              {"role":"user","content":"你好"}
#             ])

# print(response)

##
##ChatCompletion(id='bccd2e81-203b-47fd-a737-b87af3d27b25', 
# choices=[Choice(finish_reason='stop', index=0, logprobs=None, 
# message=ChatCompletionMessage(content='你好！很高兴见到你！😊\n\n我是DeepSeek，
# 一个免费的人工智能助手。无论你想聊聊天、解答学习或工作上的问题，还是需要一些生活建议，
# 我都很乐意帮忙。今天有什么我可以为你做的吗？', 
# refusal=None, role='assistant', annotations=None, audio=None, function_call=None, 
# tool_calls=None, 
# reasoning_content='好的，用户发来一个简单的问候“你好”。这是一个非常基础的社交开场。
# 用户可能刚接触我，想打个招呼，或者测试我是否存在。深层需求可能是建立连接，
# 确认我的回应是否友好和可用。\n\n我需要给出一个热情、友好的回应，表明我准备好提供帮助了。
# 可以用问候回应用户，并清楚告知我的能力和服务范围，最后以一个开放性问题鼓励用户提出具体需求。
# \n\n想到了用“你好！很高兴见到你”开头，然后简要介绍自己能做的几类事情（聊天、学习、工作），
# 最后以“我能帮你做点什么吗？”结束，这样既礼貌又明确。'))], created=1784942822,
#  model='deepseek-v4-flash', object='chat.completion', moderation=None,
#  service_tier=None, 
#  usage=CompletionUsage(completion_tokens=179, prompt_tokens=5, 
# total_tokens=184, 
# completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=None, 
# audio_tokens=None, reasoning_tokens=128, rejected_prediction_tokens=None), 
# prompt_tokens_details=PromptTokensDetails(audio_tokens=None, cache_write_tokens=None, 
# cached_tokens=0), prompt_cache_hit_tokens=0, prompt_cache_miss_tokens=5))