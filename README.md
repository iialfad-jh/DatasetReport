# DatasetReport

DatasetReport 是一个轻量 Python CLI 工具：扫描数据集文件夹中的 CSV/Excel 文件，提取基础数据质量统计，并生成一个 HTML 报告。

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

# 大文件只对前 5000 行做详细列分析，文件总行数仍会统计
datareport ./data --out report.html --sample-rows 5000
```

工具会递归扫描 `./data`，处理 `.csv`、`.xlsx` 和 `.xls` 文件，并将报告写入指定路径。

## 当前能力与限制

- 每个 Excel 文件读取第一个工作表；CSV 采用分块读取以降低内存占用。
- 文件总行数、列数、缺失值、唯一值、重复行、空列和常量列会被统计。
- 数值列提供最小值、最大值、平均值、中位数和标准差；文本列提供长度范围。
- `--sample-rows` 限制详细列分析的行数，报告会标记抽样状态。
- 单个文件读取失败不会阻止其他文件生成报告，错误会列在报告末尾。
- AI Summary 是本地占位文本，不会调用任何外部模型。
- 图表接口已预留，但当前不生成图表。

## 后续计划

- 接入 OpenAI API 生成可配置的自然语言总结。
- 使用 Plotly 添加可选交互式图表。
- 支持更多输入格式和报告模板选项。
