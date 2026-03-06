# GitHub Repository Health Analyzer
# GitHub仓库健康度分析器

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🚀 Analyze GitHub repository health metrics with beautiful visualizations and detailed reports.
> 🚀 使用精美的可视化图表和详细报告分析GitHub仓库健康度指标。

## Features | 功能特性

- 📊 **Comprehensive Metrics Analysis | 全面的指标分析**
  - Stars, Forks, Watchers tracking | 星标、分支、关注者追踪
  - Contributor activity analysis | 贡献者活动分析
  - Issue resolution metrics | 问题解决指标
  - Pull request statistics | 拉取请求统计

- 🎨 **Beautiful Visualizations | 精美可视化**
  - Interactive charts and graphs | 交互式图表
  - Health score dashboard | 健康度评分仪表板
  - Activity timeline | 活动时间线
  - HTML report generation | HTML报告生成

- 🏥 **Health Score Calculation | 健康度评分**
  - Overall repository grade (A+ to F) | 整体仓库评级（A+到F）
  - Multi-factor analysis | 多因素分析
  - Community engagement metrics | 社区参与度指标

- 🆓 **No API Key Required | 无需API密钥**
  - Uses GitHub public API | 使用GitHub公共API
  - Free for all repositories | 所有仓库免费使用

## Quick Start | 快速开始

### Installation | 安装

```bash
# Clone the repository | 克隆仓库
git clone https://github.com/chenpipi0807/github-repo-health-analyzer.git
cd github-repo-health-analyzer

# Install dependencies | 安装依赖
pip install -r requirements.txt
```

### Usage | 使用方法

```bash
# Analyze a repository | 分析一个仓库
python analyzer.py https://github.com/torvalds/linux

# Specify output directory | 指定输出目录
python analyzer.py https://github.com/microsoft/vscode --output ./reports

# Generate specific format | 生成特定格式
python analyzer.py https://github.com/facebook/react --format summary
```

### Example Output | 示例输出

```
╔══════════════════════════════════════════════════════════════╗
║          GitHub Repository Health Analysis Summary           ║
╚══════════════════════════════════════════════════════════════╝

📁 Repository: microsoft/vscode
📝 Description: Visual Studio Code

⭐ Stars: 150,000+
🍴 Forks: 25,000+
👁️ Watchers: 3,000+

🏥 Health Score: 92.5/100 - A+ 🌟

📊 Detailed Breakdown:
  • Stars Popularity: 20.0/20
  • Contributor Diversity: 18.5/20
  • Issue Resolution: 19.2/20
  • PR Merge Rate: 18.8/20
  • Recent Activity: 16.0/20
```

## Health Score Explained | 健康度评分说明

The health score (0-100) is calculated based on five key factors:
健康度评分（0-100）基于五个关键因素计算：

| Factor | Weight | Description |
|--------|--------|-------------|
| Stars Popularity | 20% | Repository popularity and reach |
| Contributor Diversity | 20% | Number of active contributors |
| Issue Resolution | 20% | Speed and rate of issue resolution |
| PR Merge Rate | 20% | Efficiency of code review process |
| Recent Activity | 20% | Commit frequency in last 90 days |

### Grading Scale | 评分等级

- **A+ (90-100)**: Excellent | 优秀 🌟
- **A (80-89)**: Good | 良好
- **B+ (70-79)**: Above Average | 高于平均
- **B (60-69)**: Average | 平均
- **C (50-59)**: Below Average | 低于平均
- **D (40-49)**: Poor | 较差
- **F (<40)**: Needs Improvement | 需要改进

## Output Files | 输出文件

After running the analyzer, you'll get three files:
运行分析器后，你将获得三个文件：

1. **`{repo}_report.html`** - Beautiful HTML report with interactive charts
   精美的HTML报告，包含交互式图表

2. **`{repo}_analysis.png`** - Visualization dashboard image
   可视化仪表板图片

3. **`{repo}_data.json`** - Raw data in JSON format
   JSON格式的原始数据

## Use Cases | 使用场景

- 🔍 **Repository Evaluation | 仓库评估**: Quickly assess open source project health
- 👥 **Contributor Analysis | 贡献者分析**: Understand community engagement
- 📈 **Trend Tracking | 趋势追踪**: Monitor repository growth over time
- 🎯 **Project Comparison | 项目对比**: Compare multiple repositories side by side

## System Requirements | 系统要求

- Python 3.8 or higher
- Internet connection (for GitHub API access)
- ~50MB disk space for outputs

## License | 许可证

MIT License - feel free to use for personal or commercial projects.
MIT许可证 - 可用于个人或商业项目。

## Contributing | 贡献

Contributions are welcome! Please feel free to submit a Pull Request.
欢迎贡献！请随时提交Pull Request。

## Author | 作者

Created with ❤️ by [chenpipi0807](https://github.com/chenpipi0807)

---

⭐ **If you find this tool helpful, please give it a star!**
⭐ **如果你觉得这个工具 helpful，请给个星标！**
