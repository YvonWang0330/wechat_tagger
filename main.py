#!/usr/bin/env python3
"""
微信好友标签化工具 - 主程序
"""
import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tagger.importer import ChatImporter, ChatMessage
from tagger.analyzer import TagAnalyzer
from tagger.ui import TagUI
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Contact:
    """联系人类"""

    def __init__(self, name: str, messages: List[ChatMessage]):
        self.name = name
        self.messages = messages
        self.tags = {}

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "name": self.name,
            "message_count": len(self.messages),
            "tags": self.tags
        }


class WeChatTagger:
    """微信好友标签化工具主类"""

    def __init__(self, config_file: str = "config.json"):
        """
        初始化工具

        Args:
            config_file: 配置文件路径
        """
        load_dotenv()

        # 加载配置
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.tag_categories = self.config.get('tags', {})

        # 初始化模块
        self.analyzer = TagAnalyzer()
        self.ui = TagUI()

        logger.info("微信好友标签化工具初始化完成")

    def import_chat(self, file_path: str) -> Dict[str, Contact]:
        """
        导入聊天记录

        Args:
            file_path: 聊天记录文件路径

        Returns:
            联系人字典 {name: Contact}
        """
        logger.info(f"开始导入聊天记录: {file_path}")

        # 导入消息
        messages = ChatImporter.import_chat(file_path)

        if not messages:
            logger.warning("未导入到任何消息")
            return {}

        # 按发送人分组
        contacts = {}
        for msg in messages:
            sender = msg.sender
            if sender not in contacts:
                contacts[sender] = Contact(sender, [])
            contacts[sender].messages.append(msg)

        logger.info(f"共发现 {len(contacts)} 个联系人")
        return contacts

    def analyze_contacts(self, contacts: Dict[str, Contact]) -> List[Contact]:
        """
        分析所有联系人的标签

        Args:
            contacts: 联系人字典

        Returns:
            已分析标签的联系人列表
        """
        results = []

        for i, (name, contact) in enumerate(contacts.items(), 1):
            logger.info(f"分析联系人 {i}/{len(contacts)}: {name}")

            # 提取消息内容
            message_contents = [msg.content for msg in contact.messages]

            # AI分析标签
            tags = self.analyzer.analyze_contact(message_contents, self.tag_categories)

            # 显示结果
            self.ui.display_tags(name, tags)

            # 用户确认
            confirmed_tags = self.ui.confirm_tags(tags)
            contact.tags = confirmed_tags
            results.append(contact)

        return results

    def export_results(self, results: List[Contact], output_file: str = "tags_result.json"):
        """
        导出标签结果

        Args:
            results: 分析结果
            output_file: 输出文件路径
        """
        output_data = {
            "total_contacts": len(results),
            "export_time": self._get_current_time(),
            "contacts": [contact.to_dict() for contact in results]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        logger.info(f"标签结果已导出到: {output_file}")

    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def run(self, input_file: str, output_file: str = "tags_result.json"):
        """
        运行标签化流程

        Args:
            input_file: 输入的聊天记录文件
            output_file: 输出的标签文件
        """
        # 1. 导入聊天记录
        contacts = self.import_chat(input_file)
        if not contacts:
            logger.error("未导入到任何联系人，程序退出")
            return

        # 2. 分析标签
        results = self.analyze_contacts(contacts)

        # 3. 显示摘要
        self.ui.display_summary(results)

        # 4. 导出结果
        self.export_results(results, output_file)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="微信好友标签化工具 - 基于AI分析聊天记录给好友打标签")
    parser.add_argument(
        "input_file",
        help="聊天记录文件路径（支持 .json 或 .txt 格式）"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="tags_result.json",
        help="输出文件路径（默认: tags_result.json）"
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="配置文件路径（默认: config.json）"
    )

    args = parser.parse_args()

    try:
        # 检查输入文件
        if not Path(args.input_file).exists():
            print(f"错误: 文件不存在 - {args.input_file}")
            sys.exit(1)

        # 运行工具
        tagger = WeChatTagger(config_file=args.config)
        tagger.run(input_file=args.input_file, output_file=args.output)

    except ValueError as e:
        logger.error(f"配置错误: {e}")
        print(f"\n错误: {e}")
        print("\n请按照以下步骤配置：")
        print("1. 复制 .env.example 为 .env")
        print("2. 填入 OpenAI API Key 到 .env 文件")
        print("3. 重新运行程序")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("程序已取消")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序异常: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
