# -*- coding: utf-8 -*-
import re
import os
import random
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox

# ======================================
# Встроенный конфиг семейств и правил
# ======================================

DEFAULT_CONFIG = {
    "families": [
        # SAM (оба борта)
        { "prefix": "patriot", "side": "blue", "class": "sam", "coldwar": "false", "variants": {
            "blue": [ {"id":"patriot", "coldwar":"false"} ]
        }},
        { "prefix": "nasams",  "side": "blue", "class": "sam", "coldwar": "false", "variants": {
            "blue": [ {"id":"nasams", "coldwar":"false"} ]
        }},
        { "prefix": "hawk",    "side": "blue", "class": "sam", "coldwar": "both", "variants": {
            "blue": [ {"id":"hawk", "coldwar":"both"} ]
        }},
        
        # AIRDEF (новое семейство)
        { "prefix": "roland",  "side": "blue", "class": "airdef", "coldwar": "both", "variants": {
            "blue": [ {"id":"roland", "coldwar":"both"} ]
        }},
        { "prefix": "rapier",  "side": "blue", "class": "airdef", "coldwar": "true", "variants": {
            "blue": [ {"id":"rapier", "coldwar":"true"} ]
        }},

        # SA-системы, разделенные по классам
        { 
            "prefix": "sa", 
            "side": "red", 
            "class": "sam", 
            "coldwar": "both", 
            "variants": {
                "red": [
                    {"id": "sa2",  "coldwar": "true"},
                    {"id": "sa3",  "coldwar": "true"},
                    {"id": "sa5",  "coldwar": "true"},
                    {"id": "sa10", "coldwar": "false"}
                ]
            }
        },
        { 
            "prefix": "sa", 
            "side": "red", 
            "class": "airdef", 
            "coldwar": "both", 
            "variants": {
                "red": [
                    {"id": "sa6",  "coldwar": "true"},
                    {"id": "sa9",  "coldwar": "both"},
                    {"id": "sa11", "coldwar": "false"},
                    {"id": "sa15", "coldwar": "false"},
                    {"id": "sa19", "coldwar": "false"}
                ]
            }
        },
        
        # INFANTRY (оба борта)
        { "prefix": "infantry", "side": "both", "class":"infantry", "coldwar":"both", "variants": {
            "red": [
                {"id":"infantry1","coldwar":"true"},
                {"id":"infantry2","coldwar":"true"},
                {"id":"infantry3","coldwar":"true"},
                {"id":"infantry4","coldwar":"false"},
                {"id":"infantry5","coldwar":"false"},
                {"id":"infantry6","coldwar":"false"}
            ],
            "blue": [
                {"id":"infantry1","coldwar":"true"},
                {"id":"infantry2","coldwar":"true"},
                {"id":"infantry3","coldwar":"true"},
                {"id":"infantry4","coldwar":"false"},
                {"id":"infantry5","coldwar":"false"},
                {"id":"infantry6","coldwar":"false"}
            ]
        }},

        # SHORAD (для обеих сторон)
        { "prefix": "shorad", "side":"both", "class":"shorad", "coldwar":"both", "variants": {
            "red": [
                {"id":"shorad1","coldwar":"true"},
                {"id":"shorad2","coldwar":"true"},
                {"id":"shorad3","coldwar":"false"},
                {"id":"shorad4","coldwar":"false"}
            ],
            "blue": [
                {"id":"shorad1","coldwar":"true"},
                {"id":"shorad2","coldwar":"true"},
                {"id":"shorad3","coldwar":"false"},
                {"id":"shorad4","coldwar":"false"}
            ]
        }},

        # AAA (только red)
        { "prefix": "aaa", "side":"red", "class":"aaa", "coldwar":"both", "variants": {
            "red": [
                {"id":"aaa1","coldwar":"true"},
                {"id":"aaa2","coldwar":"false"},
                {"id":"aaa3","coldwar":"both"}
            ]
        }},

        # EWR (по одному ID на сторону, CW = both)
        { "prefix": "ewr", "side":"both", "class":"ewr", "coldwar":"both", "variants": {
            "red":   [ {"id":"ewr","coldwar":"both"} ],
            "blue": [ {"id":"ewr","coldwar":"both"} ]
        }}
    ]
}

CLASSES = ["sam", "aaa", "infantry", "ewr", "shorad", "airdef"]
NAME_TO_CLASS = {
    'garrison': 'infantry',
    'infantry': 'infantry',
    'sam': 'sam',
    'airdef': 'airdef',
    'shorad': 'shorad',
    'aaa': 'aaa',
    'ewr': 'ewr'
}

# ==============================
# Регэкспы и парсинг init.lua
# ==============================

IS_COLD_RE  = re.compile(r'\bConfig\.isColdWar\s*=\s*true\b', re.IGNORECASE)
DEFENSES_TABLE_START_RE = re.compile(r'\bdefenses\s*=\s*\{', re.IGNORECASE)
SIDE_BLOCK_RE   = re.compile(r'\b(red|blue)\s*=\s*\{', re.IGNORECASE)
PRESET_DEF_RE   = re.compile(r'^\s*([A-Za-z0-9_]+)\s*=\s*Preset:new\s*\(', re.MULTILINE)

ZONE_BLOCK_RE = re.compile(
    r'(zones\.(\w+)\s*=\s*ZoneCommand:new\s*\(.*?defenses\s*=\s*\{.*?\}\s*\))',
    re.IGNORECASE | re.DOTALL
)

EXTEND_BLOCK_RE = re.compile(
    r'(presets\.defenses\.(red|blue)\.([A-Za-z0-9_]+)\s*:\s*extend\s*\(\s*\{.*?\}(?:\s*,\s*|(?=\s*\))))',
    re.IGNORECASE | re.DOTALL
)

ID_LINE_RE = re.compile(
    r'(presets\.defenses\.(red|blue)\.([A-Za-z0-9_]+))',
    re.IGNORECASE
)
NAME_LINE_RE = re.compile(
    r"name\s*=\s*['\"]([^'\"]+)['\"]",
    re.IGNORECASE
)

BLUE_LINE_RE = re.compile(r'^\s*local\s+blueSupply\s*=\s*\{([^\}]*)\}\s*$', re.MULTILINE)
RED_LINE_RE  = re.compile(r'^\s*local\s+redSupply\s*=\s*\{([^\}]*)\}\s*$', re.MULTILINE)

def _find_matching_brace(s: str, start_idx: int) -> int:
    depth = 0
    for i in range(start_idx, len(s)):
        if s[i] == '{': depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0: return i
    return -1

def parse_defense_catalog(text: str) -> dict:
    res = {'red': set(), 'blue': set()}
    m = DEFENSES_TABLE_START_RE.search(text)
    if not m: return res
    start = m.end() - 1
    end = _find_matching_brace(text, start)
    if end == -1: return res
    table = text[start+1:end]
    pos = 0
    while True:
        ms = SIDE_BLOCK_RE.search(table, pos)
        if not ms: break
        side = ms.group(1).lower()
        sb_start = ms.end() - 1
        while sb_start < len(table) and table[sb_start] != '{':
            sb_start += 1
        sb_end = _find_matching_brace(table, sb_start)
        if sb_end == -1: break
        side_block = table[sb_start+1:sb_end]
        for md in PRESET_DEF_RE.finditer(side_block):
            res[side].add(md.group(1).lower())
        pos = sb_end + 1
    return res

def _cw_allows(tag: str, cw_mode: str) -> bool:
    t = (tag or "both").lower()
    if cw_mode == "true":
        return t in ("true","both")
    else:
        return t in ("false","both")

def build_pools(catalog: dict, cw_mode: str):
    pools = { 'red': {c: {"variants":[]} for c in CLASSES}, 'blue': {c: {"variants":[]} for c in CLASSES} }
    id2info = {}

    for fam in DEFAULT_CONFIG["families"]:
        prefix = fam["prefix"].lower()
        fam_side = fam["side"].lower()
        fam_class= fam["class"].lower()
        variants = fam.get("variants", {})

        sides_to_fill = []
        if fam_side == "both":
            sides_to_fill = ["red","blue"]
        else:
            sides_to_fill = [fam_side]

        for side in sides_to_fill:
            fam_variants = []
            if side in variants:
                fam_variants = [v for v in variants[side]]
            else:
                for id_ in sorted(catalog.get(side, set())):
                    if id_.startswith(prefix):
                        fam_variants.append({"id": id_, "class": fam_class, "coldwar": fam.get("coldwar","both")})

            present = set(catalog.get(side, set()))
            fam_variants = [v for v in fam_variants if v["id"].lower() in present]

            filtered = []
            for v in fam_variants:
                cw_tag = v.get("coldwar") or fam.get("coldwar","both")
                if _cw_allows(cw_tag, cw_mode):
                    v_class = v.get("class") or fam_class
                    filtered.append({"id":v["id"], "class":v_class, "coldwar":cw_tag})

            if not filtered:
                continue

            for v in filtered:
                v_class = v.get("class")
                if v_class in pools[side]:
                    pools[side][v_class]["variants"].append(v)
                id2info[v["id"].lower()] = {"class":v_class, "family":prefix}

    return pools, id2info

def process_and_replace(text, rng, pools, id2info):
    new_text = text
    
    extend_block_re = re.compile(
        r'(presets\.defenses\.(red|blue)\.([A-Za-z0-9_]+)\s*:\s*extend\s*\(\s*\{.*?\}(?:\s*,\s*|(?=\s*\))))',
        re.IGNORECASE | re.DOTALL
    )

    matches = list(extend_block_re.finditer(new_text))
    
    for m in reversed(matches):
        full_match = m.group(1)
        side = m.group(2).lower()
        cur_id = m.group(3).lower()

        m_name = NAME_LINE_RE.search(full_match)
        if not m_name:
            continue
        full_name = m_name.group(1).lower()

        class_to_use = None
        for key, val in NAME_TO_CLASS.items():
            if f"-{key}-" in full_name:
                class_to_use = val
                break
        
        if not class_to_use:
            class_to_use = id2info.get(cur_id, {}).get("class")

        if not class_to_use:
            continue
            
        new_id = cur_id
        if side in pools and class_to_use in pools[side]:
            all_class_ids = [v["id"].lower() for v in pools[side][class_to_use]["variants"]]
            candidates = [x for x in all_class_ids if x != cur_id]
            if candidates:
                new_id = rng.choice(candidates)
            else:
                new_id = cur_id
        else:
            continue
        
        if new_id != cur_id:
            new_block = re.sub(
                r'(presets\.defenses\.' + re.escape(side) + r'\.)' + re.escape(cur_id) + r'\s*:?\s*extend',
                r'\1' + new_id + r':extend',
                full_match,
                count=1,
                flags=re.IGNORECASE
            )

            name_parts = full_name.split('-')
            if len(name_parts) >= 3:
                old_id_part_index = -1
                for i in range(len(name_parts)):
                    if name_parts[i] == cur_id:
                        old_id_part_index = i
                        break
                
                if old_id_part_index != -1:
                    name_parts[old_id_part_index] = new_id
                
                new_full_name = '-'.join(name_parts)
                new_block = re.sub(
                    r"name\s*=\s*['\"]" + re.escape(full_name) + r"['\"]",
                    f"name = '{new_full_name}'",
                    new_block,
                    count=1,
                    flags=re.IGNORECASE
                )
            
            new_text = new_text[:m.start()] + new_block + new_text[m.end():]
            
    return new_text

# ==============================
# Offmap-supply (BLUE <= 5; RED = зеркало + 2)
# ==============================

def _parse_list_items(list_text): return [x.strip() for x in list_text.split(',') if x.strip()]
def _format_supply(prefix, nums): return "{" + ",".join(f"'{prefix}{n}'" for n in nums) + "}"

def mirror_offmap_supply(text):
    m_blue = BLUE_LINE_RE.search(text)
    m_red  = RED_LINE_RE.search(text)
    if not m_blue or not m_red:
        return text
    
    blue_items = _parse_list_items(m_blue.group(1))
    blue_target = min(len(blue_items), 5)
    if blue_target <= 0: blue_target = 1

    pool = list(range(1, 11))
    random.shuffle(pool)
    blue_nums = sorted(pool[:blue_target])

    red_base = sorted({11 - n for n in blue_nums})
    forbidden = set(blue_nums) | set(red_base)
    want_total_red = min(len(red_base) + 2, 10)
    extra_candidates = [n for n in range(1, 11) if n not in forbidden]
    random.shuffle(extra_candidates)
    red_extras = sorted(extra_candidates[:max(0, want_total_red - len(red_base))])
    red_nums = sorted(red_base + red_extras)

    blue_line_new = f"local blueSupply = {_format_supply('offmap-supply-blue-', blue_nums)}"
    red_line_new  = f"local redSupply  = {_format_supply('offmap-supply-red-', red_nums)}"

    text = BLUE_LINE_RE.sub(blue_line_new, text, count=1)
    text = RED_LINE_RE.sub(red_line_new, text, count=1)
    return text

# ==============================
# Основной процесс
# ==============================

def process_once(text: str, rng) -> str:
    cw_mode = "true" if IS_COLD_RE.search(text) else "false"
    catalog = parse_defense_catalog(text)
    pools, id2info = build_pools(catalog, cw_mode)
    
    new_text = process_and_replace(text, rng, pools, id2info)
    new_text = mirror_offmap_supply(new_text)

    stamp = "-- randomized at " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    if not new_text.startswith("--"):
        new_text = stamp + new_text
    else:
        new_text = stamp + new_text

    return new_text, cw_mode

def main():
    root = tk.Tk(); root.withdraw()
    path = filedialog.askopenfilename(title="Выберите init.lua", filetypes=[("Lua files","*.lua")])
    if not path:
        messagebox.showerror("Ошибка", "Файл не выбран!")
        try: root.destroy()
        except Exception: pass
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            original = f.read()

        base = os.path.dirname(path)
        out_lua = os.path.join(base, "init.lua")

        rng = random.Random(int.from_bytes(os.urandom(8), 'big'))
        new_text, cw_mode = process_once(original, rng)

        with open(out_lua, "w", encoding="utf-8") as f:
            f.write(new_text)

        messagebox.showinfo(
            "Готово",
            f"Файл успешно обработан и сохранен: {out_lua}\n"
            f"Режим Cold War: {cw_mode}"
        )
    except Exception as e:
        messagebox.showerror("Произошла ошибка", f"Не удалось обработать файл: {e}")
    finally:
        try: root.destroy()
        except Exception: pass

if __name__ == "__main__":
    main()