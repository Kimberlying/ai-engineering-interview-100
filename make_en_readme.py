# make_en_readme.py

from en_build_header import en_header
from en_parts_1_2 import part1 as en_parts_1_2
from en_parts_3_4 import part3 as en_part3, part4 as en_part4
from en_parts_5_6 import part5 as en_part5, part6 as en_part6
from en_parts_7_8 import part7 as en_part7, part8 as en_part8

en_footer = """
---

## 🌟 Architectural Mindset Summary

If you only take away two mental models from this entire guide, remember:

1. **"Did the evidence ever reach the model?"**
   - If not, it is a retrieval failure; prompt tuning cannot save you.
   - If yes, but the output is wrong, it is a generation/reasoning failure; upgrading your vector DB cannot save you.
2. **"Commit to the Right Contract"**
   - Never promise verbatim word-for-word identity on stochastic systems.
   - Commit to decision stability and deterministic state machines, enforced by quantitative SLOs and regression benchmarks.

---

## 🤝 Contributing & Community

Contributions, real-world case studies, and sharper architectural mitigations are welcome!
- Found a typo or have an alternative production pattern? Open a Pull Request!
- Encountered a novel production LLM outage? Share it in the GitHub Discussions / Issues!

## 📄 License & Attribution

- Original scenario inspiration: [AI Engineering Insider](https://aiengineeringinsider.substack.com/p/the-100-questions-that-haunt-ai-engineering)
- Structured concept breakdowns, production-grade diagnostic playbooks, and end-to-end system designs curated and open-sourced by [@Kimberlying](https://github.com/Kimberlying).
- Licensed under the [MIT License](LICENSE). If this handbook helped you, consider starring ⭐️ the repo!
"""

full_en_content = (
    en_header + "\n" +
    en_parts_1_2 + "\n" +
    en_part3 + "\n" +
    en_part4 + "\n" +
    en_part5 + "\n" +
    en_part6 + "\n" +
    en_part7 + "\n" +
    en_part8 + "\n" +
    en_footer
)

with open("README_EN.md", "w", encoding="utf-8") as f:
    f.write(full_en_content)

print(f"Generated README_EN.md with {len(full_en_content)} characters and {len(full_en_content.splitlines())} lines.")
