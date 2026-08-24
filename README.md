# DatasetReport

DatasetReport 是一个轻量 Python CLI 工具：扫描数据集文件夹中的 CSV/Excel 文件，提取基础字段统计，并生成一个简单的 HTML 报告。

## 安装

需要 Python 3.11 或更高版本：

```bash
pip install -e .
```

开发依赖（包含 pytest）：

```bash
pip install -e ".[dev]"
```

## 使用

```bash
datareport ./data --out report.html
```

工具会递归扫描 `./data`，处理 `.csv`、`.xlsx` 和 `.xls` 文件，并将报告写入指定路径。

## 当前限制

- 每个 Excel 文件只读取第一个工作表。
- 目前只生成形状、dtype、缺失值和少量样本值等基础统计。
- AI Summary 是本地占位文本，不会调用任何外部模型。
- 图表接口已预留，但当前不生成图表。

## 后续计划

- 增加更丰富的字段分布和质量检查。
- 接入 OpenAI API 生成可配置的自然语言总结。
- 使用 Plotly 添加可选交互式图表。
- 支持更多输入格式和报告模板选项。

