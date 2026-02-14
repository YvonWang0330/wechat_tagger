# 微信好友标签化工具

基于AI分析微信聊天记录，自动为好友打标签（教育信息、籍贯、性格、兴趣等），支持半自动确认模式。

## 功能特点

- 🤖 **AI智能分析** - 基于GPT-4o从聊天内容提取标签
- ✅ **人工确认模式** - 每个标签都可以确认、修改或删除
- 📊 **多维度标签** - 支持教育、籍贯、性格、兴趣等分类
- 📄 **多格式支持** - 支持JSON、TXT格式的聊天记录导入
- 💾 **导出结果** - 将标签结果导出为JSON文件

## 快速开始

### 1. 安装依赖

```bash
cd wechat_tagger
pip install -r requirements.txt
```

### 2. 配置API密钥

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，填入 OpenAI API Key
nano .env
```

将 `your_openai_api_key_here` 替换为你的 OpenAI API Key。

### 3. 准备聊天记录

导出微信聊天记录，支持两种格式：

**JSON格式** - 示例：
```json
[
  {
    "sender": "张三",
    "content": "我是清华大学毕业的",
    "timestamp": "2024-01-01 10:30:00"
  }
]
```

**TXT格式** - 微信导出文本：
```
2024-01-01 10:30:00 张三: 我是清华大学毕业的
2024-01-01 10:31:00 李四: 真的吗？
```

### 4. 运行工具

```bash
python main.py 聊天记录.json
```

或指定输出文件：

```bash
python main.py 聊天记录.json -o result.json
```

## 使用流程

1. **导入聊天记录** - 工具自动解析聊天文件
2. **AI分析** - 逐个联系人分析聊天内容
3. **标签确认** - 显示AI提取的标签，你选择：
   - ✅ 确认标签
   - ✏️ 修改标签
   - ➕ 添加标签
   - ➖ 删除全部
   - ⏭️  跳过
4. **查看摘要** - 显示所有标签分布统计
5. **导出结果** - 保存为JSON文件

## 配置说明

### 环境变量 (.env)

```env
# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

### 标签分类配置 (config.json)

```json
{
  "tags": {
    "education": {
      "name": "教育信息",
      "enabled": true,
      "examples": ["博士", "硕士", "本科", "清华", "北大"]
    },
    "hometown": {
      "name": "籍贯/地域",
      "enabled": true,
      "examples": ["北京人", "上海", "广州"]
    },
    "personality": {
      "name": "性格特征",
      "enabled": true,
      "examples": ["开朗", "内向", "幽默", "稳重"]
    },
    "interests": {
      "name": "兴趣爱好",
      "enabled": true,
      "examples": ["篮球", "旅游", "电影", "游戏"]
    }
  }
}
```

可以通过修改 `config.json` 来自定义标签分类和示例。

## 输出格式

导出的JSON文件格式：

```json
{
  "total_contacts": 5,
  "export_time": "2024-01-01 12:00:00",
  "contacts": [
    {
      "name": "张三",
      "message_count": 150,
      "tags": {
        "education": ["清华", "博士"],
        "hometown": ["北京人"],
        "personality": ["开朗", "幽默"],
        "interests": ["篮球", "电影"]
      }
    }
  ]
}
```

## 参数说明

```
python main.py <input_file> [options]

位置参数:
  input_file           聊天记录文件路径（支持 .json 或 .txt）

可选参数:
  -o, --output      输出文件路径（默认: tags_result.json）
  --config           配置文件路径（默认: config.json）
  -h, --help        显示帮助信息
```

## 如何导出微信聊天记录

### 方法1: 使用微信电脑版导出

1. 打开微信电脑版
2. 找到需要分析的聊天记录
3. 右键聊天窗口 → "导出聊天记录"
4. 选择 "Word文档" 或 "文本文件" 格式

### 方法2: 使用第三方工具

- **iMazing** (Mac) - 完整备份微信数据
- **微信PC版备份** - 使用备份工具导出数据库

导出后，将聊天记录转换为工具支持的格式即可使用。

## 项目结构

```
wechat_tagger/
├── main.py              # 主程序
├── config.json          # 标签分类配置
├── requirements.txt     # Python依赖
├── .env.example        # 环境变量模板
├── .env               # 环境变量（需自行创建）
└── tagger/
    ├── __init__.py
    ├── importer.py     # 聊天记录导入
    ├── analyzer.py      # AI标签分析
    └── ui.py           # 交互界面
```

## 常见问题

### Q: AI分析不准确怎么办？

A: 使用确认模式，可以直接修改AI提取的标签。标签以你确认为准。

### Q: 支持哪些聊天记录格式？

A: 目前支持 JSON 和 TXT 格式。如果你的聊天记录是其他格式，可以先转换。

### Q: API调用会消耗很多吗？

A: GPT-4o-mini很便宜，分析100个联系人大约花费 $0.1-$0.5。

### Q: 可以自定义标签分类吗？

A: 可以，修改 `config.json` 中的 `tags` 部分即可。

## License

MIT License
