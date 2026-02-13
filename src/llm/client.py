import os
import json
from openai import OpenAI

class DeepSeekClient:
    def __init__(self, api_key=None):
        """
        初始化 DeepSeek 客户端。
        推荐将 API Key 写在系统环境变量里，或者在测试时直接传入。
        """
        # 如果代码里没传，就去环境变量找 DEEPSEEK_API_KEY
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 API Key！请传入 api_key 或设置 DEEPSEEK_API_KEY 环境变量。")
        
        # DeepSeek 的接口地址完全兼容 OpenAI SDK
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        
    def get_decision(self, system_prompt, user_prompt, model="deepseek-chat"):
        """
        向大模型发送请求，获取顾客的购买决策
        """
        try:
            # 调用 API
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                # 设置 response_format 为 json_object 可以强制要求模型输出 JSON 
                # (注意：提示词里必须也提到 "json" 单词，咱们前面已经写了)
                response_format={"type": "json_object"},
                temperature=0.7,  # 0.7 给予一定的随机性，符合人类消费的非绝对理性
                max_tokens=200    # 决策结果很短，限制 token 节省成本和时间
            )
            
            # 获取模型返回的纯文本
            raw_content = response.choices[0].message.content
            
            # 解析并返回 Python 字典
            return self._parse_json(raw_content)
            
        except Exception as e:
            print(f"❌ API 调用失败: {e}")
            # 如果出错（比如网络断了），返回一个默认的不购买决策，防止程序崩溃
            return {"decision": "None", "reason": "API_ERROR"}

    def _parse_json(self, text):
        """
        内部辅助方法：清理 LLM 返回的文本并解析为 JSON。
        即便开启了 json_object，有时模型也会加上 ```json ``` 的 Markdown 标记。
        """
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            print(f"❌ JSON 解析失败，原始文本:\n{text}")
            return {"decision": "None", "reason": "JSON_PARSE_ERROR"}

# --- 简单测试逻辑 ---
if __name__ == "__main__":
    # ⚠️ 替换为你自己在 deepseek 官网申请的真实 API KEY ⚠️
    TEST_API_KEY = "sk-d6389f6e995543959b1c313cf2ffd778" 
    
    # 这里我们手写一段咱们之前生成的 Prompt 进行测试
    test_sys_prompt = "你是一个生活在上海的25-34岁人群，职业是Tech/Finance。你的月收入大约25000元。你对咖啡价格敏感度为Low。你平时最喜欢喝Latte。如果是工作时间，你倾向于就近购买或外卖。"
    test_user_prompt = """
    现在位置: (1000, 1000)。
    可选方案如下：
    【选项 S1_Walk】步行去 Starbucks (自提)
       - 最终价: 32.0元 | 距离: 50米
    【选项 S2_Delivery】点 Luckin (外卖)
       - 最终价: 13.0元 (含运费: 3元)
       - 等待: 30 分钟
    【选项 None】不买了

    【决策任务】
    请基于你的人设做出选择。请返回 JSON: { "decision": "...", "reason": "..." }
    """

    print("🤖 正在呼叫 DeepSeek 大脑思考中...")
    
    try:
        client = DeepSeekClient(api_key=TEST_API_KEY)
        result = client.get_decision(test_sys_prompt, test_user_prompt)
        print("\n✅ DeepSeek 决策结果：")
        print(f"最终选择: {result.get('decision')}")
        print(f"内心OS  : {result.get('reason')}")
    except Exception as e:
        print(f"测试出错，请检查 API Key 是否正确: {e}")