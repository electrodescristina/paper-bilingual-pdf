#!/usr/bin/env python3
"""Audit source coverage and exported rendered geometry; does not inspect PDFs."""
import argparse
import json
import math
from pathlib import Path

KINDS = {'paragraph', 'heading', 'caption', 'table', 'footnote', 'reference',
         'list_item', 'figure', 'equation', 'identifier'}


def indexed(rows, label, errors):
    if not isinstance(rows, list):
        raise ValueError(f'{label} must be an array')
    result = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get('id'), str) or not row['id'].strip():
            raise ValueError(f'{label} contains an invalid ID')
        if row['id'] in result:
            errors.append(f'Duplicate {label} ID: {row["id"]}')
        result[row['id']] = row
    return result


def rectangle(value, label):
    if (not isinstance(value, list) or len(value) != 4 or
            any(isinstance(v, bool) or not isinstance(v, (int, float)) or
                not math.isfinite(v) for v in value)):
        raise ValueError(f'{label} must contain four finite coordinates')
    if value[0] >= value[2] or value[1] >= value[3]:
        raise ValueError(f'{label} has zero or negative area')
    return value


def audit(source, layout, tolerance=0.75):
    if not isinstance(source, dict) or not isinstance(layout, dict):
        raise ValueError('Both input files must contain objects')
    if not math.isfinite(tolerance) or tolerance < 0 or tolerance > 1:
        raise ValueError('Tolerance must be between 0 and 1 pt')
    errors = []
    original = indexed(source.get('units'), 'source unit', errors)
    translated = indexed(layout.get('units'), 'output unit', errors)
    items = indexed(layout.get('items'), 'rendered item', errors)
    if not original:
        errors.append('Source inventory is empty')
    for uid in sorted(original.keys() - translated.keys()):
        errors.append(f'Missing output unit: {uid}')
    for uid in sorted(translated.keys() - original.keys()):
        errors.append(f'Unknown output unit: {uid}')
    for uid, unit in original.items():
        if unit.get('kind') not in KINDS:
            raise ValueError(f'Unsupported source kind: {uid}')
    for uid, unit in translated.items():
        if unit.get('reviewed') is not True:
            errors.append(f'Content review unfinished: {uid}')
        status = unit.get('status')
        if status == 'translated':
            text = unit.get('translation')
            if not isinstance(text, str) or not text.strip():
                errors.append(f'Empty translation: {uid}')
            elif '\ufffd' in text:
                errors.append(f'Replacement character in translation: {uid}')
        elif status == 'preserved':
            if original.get(uid, {}).get('kind') not in {'figure', 'equation', 'identifier'}:
                errors.append(f'Prose cannot be marked preserved: {uid}')
        else:
            errors.append(f'Unfinished or unknown translation status: {uid}')
    covered = {'en': set(), 'zh': set()}
    unit_pages = {uid: {'en': set(), 'zh': set()} for uid in original}
    panels = {}
    for iid, item in items.items():
        page, side = item.get('page'), item.get('side')
        if isinstance(page, bool) or not isinstance(page, int) or page < 1 or side not in covered:
            raise ValueError(f'Invalid page or side: {iid}')
        if item.get('kind') not in {'text', 'equation', 'figure', 'table', 'page', 'identifier'}:
            raise ValueError(f'Invalid rendered kind: {iid}')
        ids = item.get('unit_ids')
        if not isinstance(ids, list) or not ids or any(not isinstance(u, str) for u in ids):
            raise ValueError(f'Invalid source mapping: {iid}')
        if len(ids) != len(set(ids)):
            errors.append(f'Duplicate source mapping within item: {iid}')
        for uid in ids:
            if uid not in original:
                errors.append(f'Unknown source mapping: {iid} -> {uid}')
            else:
                unit_pages[uid][side].add(page)
        covered[side].update(ids)
        r = rectangle(item.get('bbox'), f'{iid}.bbox')
        panel = rectangle(item.get('panel_bbox'), f'{iid}.panel_bbox')
        panels.setdefault(page, {'en': set(), 'zh': set()})[side].add(tuple(panel))
        if (r[0] < panel[0] - tolerance or r[1] < panel[1] - tolerance or
                r[2] > panel[2] + tolerance or r[3] > panel[3] + tolerance):
            errors.append(f'Content outside panel: {iid}')
    for side in covered:
        for uid in sorted(original.keys() - covered[side]):
            errors.append(f'Missing {side} placement: {uid}')
    for uid, sides in unit_pages.items():
        if sides['en'] and sides['zh'] and not sides['en'].intersection(sides['zh']):
            errors.append(f'No shared comparison page for unit: {uid}')
    for page, sides in panels.items():
        if sides['en'] and sides['zh']:
            if max(r[2] for r in sides['en']) > min(r[0] for r in sides['zh']) + tolerance:
                errors.append(f'English/Chinese panels are reversed or overlap on page {page}')
    allowed = set()
    exceptions = layout.get('allowed_overlaps', [])
    if not isinstance(exceptions, list):
        raise ValueError('allowed_overlaps must be an array')
    for entry in exceptions:
        if not isinstance(entry, dict):
            raise ValueError('Invalid overlap exception')
        pair, reason = entry.get('items'), entry.get('reason')
        if (not isinstance(pair, list) or len(pair) != 2 or
                any(not isinstance(x, str) or x not in items for x in pair) or
                pair[0] == pair[1] or not isinstance(reason, str) or not reason.strip()):
            raise ValueError('Overlap exceptions need two known IDs and a reason')
        allowed.add(frozenset(pair))
    groups = {}
    for item in items.values():
        groups.setdefault((item['page'], item['side']), []).append(item)
    for (page, side), group in groups.items():
        group.sort(key=lambda x: x['bbox'][1])
        for i, first in enumerate(group):
            a = first['bbox']
            for second in group[i + 1:]:
                b = second['bbox']
                if b[1] >= a[3] - tolerance:
                    break
                dx = min(a[2], b[2]) - max(a[0], b[0])
                dy = min(a[3], b[3]) - max(a[1], b[1])
                if dx > tolerance and dy > tolerance and frozenset((first['id'], second['id'])) not in allowed:
                    errors.append(f'Overlap on page {page} ({side}): {first["id"]} / {second["id"]}')
    return {'passed': not errors, 'source_units': len(original), 'rendered_items': len(items),
            'errors': errors, 'limits': 'Checks supplied records only; does not verify translation accuracy, PDF glyphs, or source inventory completeness.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('layout', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    try:
        result = audit(json.loads(args.source.read_text(encoding='utf-8-sig')),
                       json.loads(args.layout.read_text(encoding='utf-8-sig')))
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(f'Invalid audit input: {exc}')
        return 2
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.report:
        args.report.write_text(rendered + '\n', encoding='utf-8')
    print(rendered)
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
