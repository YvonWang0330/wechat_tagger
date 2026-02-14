"""
AI标签分析模块
"""
import os
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TagAnalyzer:
    """标签分析器 - 使用AI从聊天内容中提取标签"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        初始化分析器

        Args:
            api_key: OpenAI API密钥，如果为None则从环境变量读取
            model: 使用的模型
        """
        load_dotenv()

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未设置OPENAI_API_KEY，请在.env文件中配置")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model

        logger.info(f"AI分析器初始化完成，模型: {model}")

    def analyze_contact(
        self,
        messages: List[str],
        tag_categories: Dict
    ) -> Dict[str, List[str]]:
        """
        分析联系人聊天记录，提取标签

        Args:
            messages: 聊天消息内容列表
            tag_categories: 标签分类配置

        Returns:
            标签字典，格式: {category: [tags]}
        """
        # 构建分类描述
        category_desc = []
        for key, config in tag_categories.items():
            if config.get('enabled', True):
                desc = f"- {config['name']}"
                if 'examples' in config:
                    desc += f" (例如: {', '.join(config['examples'][:3])})"
                category_desc.append(desc)

        category_desc_str = "\n".join(category_desc)

        # 构建提示词
        system_prompt = f"""你是一个专业的社交关系分析助手，擅长从聊天记录中提取人物特征信息。

你的任务是从聊天记录中分析联系人，并给TA打上合适的标签。

标签分类包括：
{category_desc}

分析规则：
1. 基于聊天内容，提取明确提及的信息
2. 对于模糊信息，使用合理的推断
3. 标签要简洁，每个分类不超过3个标签
4. 不要编造没有依据的信息
5. 优先使用提取到的具体信息（如"985"而不是"高学历"）
6. 如果某个分类没有足够信息，返回"无"或"暂不确定"

输出格式（JSON）：
{{
  "education": ["标签1", "标签2"],
  "hometown": ["标签1"],
  "personality": ["标签1", "标签2", "标签3"],
  "interests": ["标签1", "标签2"]
}}

如果某个分类无法确定，对应的值为空数组[]。
"""

        # 准备聊天记录摘要（取前50条）
        chat_summary = "\n".join(messages[:50])

        user_prompt = f"""请分析以下聊天记录，提取联系人的标签信息：

聊天记录：
---
{chat_summary}
---

请以JSON格式返回标签分析结果。"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result_text = response.choices[0].message.content

            # 解析JSON结果
            import json
            tags = json.loads(result_text)

            # 确保所有分类都存在
            for category in tag_categories.keys():
                if category not in tags:
                    tags[category] = []

            logger.info(f"标签分析完成: {tags}")
            return tags

        except Exception as e:
            logger.error(f"AI分析失败: {e}")
            return {
                "education": [],
                "hometown": [],
                "personality": [],
                "interests": []
            }

    def get_analysis_summary(self, tags: Dict) -> str:
        """
        生成标签分析的摘要说明

        Args:
            tags: 标签字典

        Returns:
            摘要文本
        """
        summary_parts = []

        for category, tag_list in tags.items():
            if tag_list:
                summary_parts.append(f"  • {category}: {', '.join(tag_list)}")

        if summary_parts:
            return "\n".join(summary_parts)
        else:
            return "  暂未提取到有效标签"
