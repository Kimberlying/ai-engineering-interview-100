# make_readme.py

import os
from build_readme import header
from parts_1_to_2 import part1 as parts_1_2
from parts_3_to_4 import part3, part4
from parts_5_to_6 import part5, part6
from parts_7_to_8 import part7, part8

footer = """
---

## 🌟 答题心智模型总结

如果读完全文你只想带走两个核心思维，请牢记：

1. **“证据送到了没有？”**
   - 没送到是检索问题，调 Prompt 救不了；送到了还答错是生成问题，换向量库救不了。
2. **“承诺正确的事”**
   - 不承诺非确定性系统产生字字相同的措辞；承诺决策与业务状态机的一致性，用基准测试集和量化 SLO 作为团队契约。

---

## 🤝 贡献与共建

欢迎提交 Issue 或 Pull Request 补充更多真实工业级场景与排障方案！
- 发现错别字或更优工程方案？欢迎提 PR！
- 遇到了新的奇葩线上 LLM 故障？欢迎在 Issues 讨论区开帖分享！

## 📄 版权与致谢

- 原始题目场景灵感来源于：[AI Engineering Insider](https://aiengineeringinsider.substack.com/p/the-100-questions-that-haunt-ai-engineering)
- 结构化考点剖析、工业级排障路径与综合系统设计方案由 [@Kimberlying](https://github.com/Kimberlying) 整理打磨并开源。
- 遵循 [MIT License](LICENSE)。如果对你有帮助，欢迎点个 ⭐️ **Star** 支持！
"""

full_content = header + "\n" + parts_1_2 + "\n" + part3 + "\n" + part4 + "\n" + part5 + "\n" + part6 + "\n" + part7 + "\n" + part8 + "\n" + footer

with open("README.md", "w", encoding="utf-8") as f:
    f.write(full_content)

print(f"Generated README.md with {len(full_content)} characters and {len(full_content.splitlines())} lines.")
