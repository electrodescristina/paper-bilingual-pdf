# 论文中英对照 PDF Skill

一个用于制作和修复学术论文左右中英对照 PDF 的 Codex skill：默认左英文、右简体中文，强调术语准确、逻辑段落对应、公式与图像保真，以及交付前的完整性检查。

A Codex skill for English–Simplified Chinese academic paper translation, aligned PDF layout, and quality checks.

## 解决什么问题

- **术语和语义错误**：先建立本篇术语表，再核对每段的条件、否定、比较对象、数值与实验限制。
- **左右分页错配**：恢复原文逻辑阅读顺序，两侧按对应单元共享分页决定。
- **公式和图片错位**：检查根号、分数、矩阵、上下标，以及图片、图例、图注的相对位置。
- **检查不充分**：将内容覆盖、语义复核和实际渲染检查分开，不把“文件成功生成”视为完成。

支持完整原页并排和按对应单元重排两种策略。双栏原稿、跨页段落、长表格等场景需要选择适合的版式，不以保持原页数为首要目标。

## 安装

将本仓库作为 `paper-bilingual-pdf` 文件夹放入你的个人 skills 目录，确保该文件夹内直接包含 `SKILL.md`。

使用默认个人目录时，可以执行：

**Windows PowerShell**

```powershell
git clone https://github.com/electrodescristina/paper-bilingual-pdf.git "$env:USERPROFILE/.codex/skills/paper-bilingual-pdf"
```

**macOS / Linux**

```bash
git clone https://github.com/electrodescristina/paper-bilingual-pdf.git "${CODEX_HOME:-$HOME/.codex}/skills/paper-bilingual-pdf"
```

如果设置了自定义 `CODEX_HOME`，请使用其中的 `skills` 目录。如果同名 skill 已存在，先比较或备份后再更新。

## 使用

提供原始论文 PDF，并在支持此 skill 的环境中请求：

> 使用 $paper-bilingual-pdf，将这篇论文制作成完整的左英文、右简体中文对照 PDF。先统一术语，保留全部章节、公式、图表、图注和参考文献，检查逐段对应、跨页衔接、遗漏和乱码后交付。

修复已有版本时，同时提供原稿与待修复文件：

> 使用 $paper-bilingual-pdf，对照原论文修复这份中英对照 PDF，重点检查术语、翻译遗漏、左右分页和图像位置。说明实际修复内容及仍未解决的问题。

## 文件说明

| 文件 | 用途 |
|---|---|
| [SKILL.md](SKILL.md) | 翻译、布局选择和交付检查的主要规则 |
| [计算机视觉术语](references/cv-terminology.md) | 常见术语与 SIFT 等论文中的易错语义 |
| [排版与检查](references/layout-and-qa.md) | 双栏重组、共享分页、文字覆盖和实际渲染检查 |
| [检查数据格式](references/audit-format.md) | 原文清单、译文映射及实际位置记录的格式 |
| [检查工具](scripts/audit_layout.py) | 检查清单缺项、未复核条目、越界、重叠及双侧位置 |
| [测试](tests/test_audit_layout.py) | 检查工具的成功、失败和无效输入场景 |

## 检查工具

工具仅使用 Python 标准库。先按[数据格式](references/audit-format.md)准备基于真实原稿和最终排版结果的两个 JSON 文件，再运行：

```bash
python scripts/audit_layout.py source-inventory.json rendered-layout.json --report audit-result.json
```

返回码：`0` 表示所覆盖的结构检查通过，`1` 表示检查发现问题，`2` 表示输入格式错误。

运行测试：

```bash
python -m unittest discover -s tests -v
```

## 能力边界

这是指导 agent 工作的 skill，附带一个结构检查工具；它不是独立的 PDF 翻译引擎。实际翻译和 PDF 处理仍依赖使用它的模型与环境。

检查工具不直接读取 PDF，不能证明译文正确、字形完整或原文清单无遗漏。它检查的是提供的记录；语义复核和逐页检查最终渲染仍必须实际执行。规则可以提高过程的一致性，但不能保证任意模型都能达到同样的翻译质量。
