# 可选结构检查工具

`scripts/audit_layout.py` 使用 Python 标准库，不需要安装 PDF 库。它读取排版程序导出的记录，**不读取 PDF，也不自行验证记录的真实性**。原文内容清单必须在翻译前依据实际原稿建立，位置数据必须来自最终排版/渲染结果；不能从译文反推原文清单。

运行：

```text
python scripts/audit_layout.py source-inventory.json rendered-layout.json --report audit-result.json
```

成功返回 0，发现缺项、未复核、越界或重叠返回 1，输入格式错误返回 2。检查结果不能代替术语复核和逐页视觉检查。

## 输入示例

原文清单：

```json
{
  "units": [
    {"id": "p1.paragraph1", "kind": "paragraph"},
    {"id": "equation1", "kind": "equation"}
  ]
}
```

原文 unit 可额外记录 `source_pages`、`source_fragments`、原文文字和标题层级，以供人工核对。`id` 全文唯一。`kind` 是 paragraph、heading、caption、table、footnote、reference、list_item、figure、equation 或 identifier。

输出记录：

```json
{
  "units": [
    {"id": "p1.paragraph1", "status": "translated", "translation": "示例译文。", "reviewed": true},
    {"id": "equation1", "status": "preserved", "reviewed": true}
  ],
  "items": [
    {"id": "en-page1", "unit_ids": ["p1.paragraph1", "equation1"], "page": 1, "side": "en", "kind": "page", "bbox": [0, 0, 600, 800], "panel_bbox": [0, 0, 600, 800]},
    {"id": "zh-p1-line1", "unit_ids": ["p1.paragraph1"], "page": 1, "side": "zh", "kind": "text", "bbox": [650, 60, 1100, 74], "panel_bbox": [620, 0, 1220, 800]},
    {"id": "zh-eq1", "unit_ids": ["equation1"], "page": 1, "side": "zh", "kind": "equation", "bbox": [740, 95, 980, 135], "panel_bbox": [620, 0, 1220, 800]}
  ],
  "allowed_overlaps": []
}
```

坐标统一为页面左上角原点、向右/向下递增的 PDF 点数；不能混用像素与点。`page` 是实际输出页码，从 1 开始。

- `bbox` 是最终内容的实际包围盒，不是预留文本框。多行文字优先逐行记录，减少段落空白造成的误报；同一 unit 可关联多行或多个页片段。
- `panel_bbox` 是该项允许占用的左右面板区域。`side` 是逻辑上的英文或中文面板，不是文本是否只含某一种字符。
- 原页完整嵌入时，可用一个 `kind: page` 项覆盖该原页所有英文单位，不再重复登记其中的各文本行。
- `preserved` 仅适用于 equation、figure、identifier。图中的自然语言标签仍要依据主流程处理；该状态不豁免图注翻译或图内标签检查。
- `reviewed` 只在实际完成该单位内容复核后设为 true。脚本不能替人作出这个判断。
- 允许图内标注叠加时，添加 `{"items":["figure-id","label-id"],"reason":"翻译后的轴标签覆盖原轴标签，已检查未遮挡刻度"}`。必须逐对说明；不得给正文重叠添加借口来绕过修复。

工具核对原文单位的去向、双侧映射、复核状态、位置合法性、越界和非预期重叠。默认 0.75 pt 的碰撞容差仅用于字体包围盒微小接触；若遇到误报，先检查真实字形与包围盒精度，不要增大容差来掩盖错位。
