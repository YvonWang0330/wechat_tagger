"""
交互确认界面模块
"""
from typing import Dict, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
import questionary
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TagUI:
    """标签交互界面"""

    def __init__(self):
        self.console = Console()

    def display_tags(self, contact_name: str, tags: Dict) -> None:
        """
        显示标签分析结果

        Args:
            contact_name: 联系人名称
            tags: 标签字典
        """
        self.console.print(f"\n👤 联系人: [bold cyan]{contact_name}[/bold cyan]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("分类", style="cyan")
        table.add_column("标签", style="green")

        has_tags = False
        for category, tag_list in tags.items():
            if tag_list:
                table.add_row(category, ", ".join(tag_list))
                has_tags = True

        if has_tags:
            self.console.print(table)
        else:
            self.console.print("[yellow]暂未提取到标签[/yellow]")

    def confirm_tags(self, tags: Dict) -> Dict:
        """
        确认并修正标签

        Args:
            tags: AI分析出的标签

        Returns:
            确认后的标签
        """
        confirmed_tags = {}

        for category, tag_list in tags.items():
            if not tag_list:
                confirmed_tags[category] = []
                continue

            # 显示当前标签
            self.console.print(f"\n[bold]分类: {category}[/bold]")
            self.console.print(f"AI提取的标签: [green]{', '.join(tag_list)}[/green]")

            # 询问用户操作
            action = questionary.select(
                "请选择操作:",
                choices=[
                    "✅ 确认标签",
                    "✏️  修改标签",
                    "➕ 添加标签",
                    "➖ 删除全部",
                    "⏭️  跳过此分类"
                ],
                default="✅ 确认标签"
            ).ask()

            if action == "✅ 确认标签":
                confirmed_tags[category] = tag_list

            elif action == "✏️  修改标签":
                new_tags = self._edit_tags(tag_list)
                confirmed_tags[category] = new_tags

            elif action == "➕ 添加标签":
                add_tag = Prompt.ask("请输入要添加的标签", default="")
                if add_tag:
                    confirmed_tags[category] = tag_list + [add_tag]
                else:
                    confirmed_tags[category] = tag_list

            elif action == "➖ 删除全部":
                confirmed_tags[category] = []

            elif action == "⏭️  跳过此分类":
                confirmed_tags[category] = []

        return confirmed_tags

    def _edit_tags(self, current_tags: List[str]) -> List[str]:
        """
        编辑标签列表

        Args:
            current_tags: 当前标签列表

        Returns:
            编辑后的标签列表
        """
        self.console.print("\n当前标签:", ", ".join(current_tags))
        new_tag_str = Prompt.ask("请输入新的标签（用逗号分隔）", default=", ".join(current_tags))

        # 分割并清理
        new_tags = [tag.strip() for tag in new_tag_str.split(",") if tag.strip()]
        return new_tags

    def display_summary(self, results: List[Dict]) -> None:
        """
        显示分析摘要

        Args:
            results: 所有联系人的标签结果
        """
        self.console.print("\n")
        panel = Panel(
            f"✅ 已完成 [bold]{len(results)}[/bold] 个联系人的标签分析",
            title="分析完成",
            border_style="green"
        )
        self.console.print(panel)

        # 统计标签分布
        all_tags = {}
        for result in results:
            tags = result.get('tags', {})
            for category, tag_list in tags.items():
                for tag in tag_list:
                    if tag not in all_tags:
                        all_tags[tag] = []
                    all_tags[tag].append(result.get('name', '未知'))

        if all_tags:
            self.console.print("\n[bold]📊 标签分布:[/bold]")
            for tag, contacts in sorted(all_tags.items(), key=lambda x: len(x[1]), reverse=True):
                self.console.print(f"  • {tag}: {len(contacts)}人")
