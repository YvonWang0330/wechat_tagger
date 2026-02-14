"""
聊天记录导入模块
支持多种微信聊天记录格式
"""
import json
import re
from typing import List, Dict, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatMessage:
    """聊天消息类"""

    def __init__(self, sender: str, content: str, timestamp: str = ""):
        self.sender = sender  # 发送人
        self.content = content  # 消息内容
        self.timestamp = timestamp  # 时间戳

    def to_dict(self) -> Dict:
        return {
            "sender": self.sender,
            "content": self.content,
            "timestamp": self.timestamp
        }


class ChatImporter:
    """聊天记录导入器"""

    @staticmethod
    def from_json_file(file_path: str) -> List[ChatMessage]:
        """
        从JSON文件导入聊天记录

        支持格式：
        1. 微信电脑版导出格式
        2. 自定义JSON格式

        Args:
            file_path: JSON文件路径

        Returns:
            聊天消息列表
        """
        messages = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 尝试不同的JSON结构
            if isinstance(data, list):
                # 直接是消息列表
                for item in data:
                    sender = item.get('sender', item.get('from', ''))
                    content = item.get('content', item.get('message', ''))
                    timestamp = item.get('timestamp', item.get('time', ''))

                    if sender and content:
                        messages.append(ChatMessage(sender, content, timestamp))

            elif isinstance(data, dict):
                # 可能是分组的格式
                if 'messages' in data:
                    for item in data['messages']:
                        sender = item.get('sender', '')
                        content = item.get('content', '')
                        timestamp = item.get('timestamp', '')

                        if sender and content:
                            messages.append(ChatMessage(sender, content, timestamp))
                elif 'chat' in data:
                    for item in data['chat']:
                        sender = item.get('sender', '')
                        content = item.get('content', '')
                        timestamp = item.get('timestamp', '')

                        if sender and content:
                            messages.append(ChatMessage(sender, content, timestamp))

            logger.info(f"从JSON文件导入 {len(messages)} 条消息")
            return messages

        except Exception as e:
            logger.error(f"导入JSON文件失败: {e}")
            return []

    @staticmethod
    def from_txt_file(file_path: str) -> List[ChatMessage]:
        """
        从文本文件导入聊天记录

        支持格式：
        1. 微信导出文本格式（时间 + 姓名: 消息）

        Args:
            file_path: 文本文件路径

        Returns:
            聊天消息列表
        """
        messages = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 微信文本格式示例：
            # 2024-01-01 10:30:00 张三: 你好
            pattern = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(.+?):\s*(.+)'

            for match in re.finditer(pattern, content):
                timestamp = match.group(1)
                sender = match.group(2).strip()
                message_content = match.group(3).strip()

                if sender and message_content:
                    messages.append(ChatMessage(sender, message_content, timestamp))

            logger.info(f"从文本文件导入 {len(messages)} 条消息")
            return messages

        except Exception as e:
            logger.error(f"导入文本文件失败: {e}")
            return []

    @staticmethod
    def import_chat(file_path: str) -> List[ChatMessage]:
        """
        根据文件扩展名自动选择导入方式

        Args:
            file_path: 文件路径

        Returns:
            聊天消息列表
        """
        path = Path(file_path)

        if not path.exists():
            logger.error(f"文件不存在: {file_path}")
            return []

        extension = path.suffix.lower()

        if extension == '.json':
            return ChatImporter.from_json_file(file_path)
        elif extension in ['.txt', '.log']:
            return ChatImporter.from_txt_file(file_path)
        else:
            logger.warning(f"不支持的文件格式: {extension}")
            return []
