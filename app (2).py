"""Daily Words (G2) — Streamlit version.

The original app screen (daily_words.html) is shown inside Streamlit as it is.
Python does the data work on the server:
  1) reads the word library voca_3000.csv
     (번호, 단어, 뜻, 수준, 함께 알아둘 파생어 (뜻), 예문),
  2) turns 수준 into Level 1/2/3 (초등 → 1, 중·고 공통 → 2, 고교 선택 → 3),
  3) builds a fill-in-the-blank question and step-by-step hints for every word,
  4) puts the data into the page and shows it with st.components.v1.html.

Files in the repository:
  app.py, daily_words.html, voca_3000.csv, requirements.txt   (required)
  original_words.json  (optional: the 20 original items with grammar notes)
  audio.json           (optional: recorded pronunciation clips)
"""
import csv
import json
import math
import random
import re
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

BASE = Path(__file__).parent
APP_HEIGHT = 920  # height of the app screen inside Streamlit (px)
LEVEL_MAP = {"초등": 1, "중·고 공통": 2, "고교 선택": 3}

st.set_page_config(page_title="Daily Words", page_icon="📘", layout="centered")

# Hide Streamlit's own header/footer so only the app screen is visible.
st.markdown(
    """<style>
    .stApp{background:#edf1fa}
    header[data-testid="stHeader"],footer,#MainMenu{display:none}
    .block-container{padding:.6rem .4rem 0;max-width:720px}
    iframe{display:block;border:0}
    </style>""",
    unsafe_allow_html=True,
)


def find_file(name):
    """Find a file next to app.py, ignoring upper/lower case (Voca_3000.csv also works)."""
    exact = BASE / name
    if exact.exists():
        return exact
    for path in BASE.iterdir():
        if path.name.lower() == name.lower():
            return path
    return None


def read_json(name, default):
    path = find_file(name)
    if path is None:
        return default
    with path.open(encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------
# Word library (CSV)
# ------------------------------------------------------------------
def split_top_level(text):
    """Split 'a (x, y), b (z)' on commas that are not inside brackets."""
    parts, depth, cur = [], 0, ""
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def parse_family(text):
    """'disabled (장애가 있는)' -> [{'w': 'disabled', 'pos': '장애가 있는'}]"""
    family = []
    for part in split_top_level(text or ""):
        m = re.match(r"^(.*?)\s*\((.*)\)\s*$", part)
        word, meaning = (m.group(1), m.group(2)) if m else (part, "")
        family.append({"w": word.strip(), "pos": meaning.strip()})
    return family


def find_in_sentence(sentence, forms):
    """Return the exact text of the first form that appears as a whole word."""
    for form in forms:
        m = re.search(r"(?<![A-Za-z])" + re.escape(form) + r"(?![A-Za-z])", sentence, re.I)
        if m:
            return m.group(0)
    return None


def load_library():
    path = find_file("voca_3000.csv")
    if path is None:
        st.error("단어 라이브러리 파일(voca_3000.csv)을 찾을 수 없어요. app.py와 같은 폴더에 올려 주세요.")
        st.stop()
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    missing = [c for c in ("단어", "뜻", "수준", "예문") if not rows or c not in rows[0]]
    if missing:
        st.error(f"{path.name}에 필요한 열이 없어요: {', '.join(missing)}. 새 voca_3000.csv로 교체해 주세요.")
        st.stop()
    family_col = next((c for c in rows[0] if c.startswith("함께 알아둘")), None)

    words = []
    for row in rows:
        forms = [x.strip() for x in row["단어"].split("/") if x.strip()]  # advertize / advertise
        sentence = (row.get("예문") or "").strip()
        words.append({
            "word": forms[0],
            "level": LEVEL_MAP.get(row["수준"].strip(), 2),
            "pos": "",
            "meaning": row["뜻"].strip(),
            "family": parse_family(row.get(family_col, "")) if family_col else [],
            "variation": forms[1:],
            "ex": sentence,
            "exForm": find_in_sentence(sentence, forms) or forms[0],
            "exampleSource": "library",
        })
    return words


# ------------------------------------------------------------------
# Fill-in-the-blank questions and hints
# ------------------------------------------------------------------
def scramble(answer):
    """Shuffle the letters of the answer (always different from the answer)."""
    letters = list(answer.replace(" ", ""))
    rng = random.Random(answer)  # same word -> same scramble
    for _ in range(10):
        rng.shuffle(letters)
        if "".join(letters) != answer.replace(" ", ""):
            break
    return letters


def make_hints(w, answer, is_original):
    """Hints from weakest to strongest. Only hints that exist for the word are added."""
    word = w["word"]
    n = len(answer)
    hints = []

    # The answer is a changed form of the headword (preparing ← prepare, decision ← decide)
    if is_original and answer.lower() != word.lower():
        hints.append(dict(id="base", icon="🌱", label="기본 단어",
                          text=f"기본 단어는 {word}({w['meaning']})예요. 문장에 맞는 형태로 바꿔 써 보세요."))

    hints.append(dict(id="length", icon="📏", label="글자 수", text=f"{n}글자 단어예요."))
    hints.append(dict(id="first", icon="🔤", label="첫 글자", text=f"‘{answer[0]}’(으)로 시작해요."))

    related = [f["w"] + (f" ({f['pos']})" if f.get("pos") else "")
               for f in w.get("family", []) if f["w"].lower() != answer.lower()]
    if related:
        hints.append(dict(id="related", icon="🔗", label="관련 단어",
                          text="함께 알아 두면 좋은 단어: " + ", ".join(related)))

    hints.append(dict(id="sound", icon="🔊", label="발음 듣기",
                      text="소리를 듣고 철자를 떠올려 보세요.", say=answer))

    if n >= 4:
        hints.append(dict(id="last", icon="🔚", label="끝 글자", text=f"‘{answer[-1]}’(으)로 끝나요."))
    if n >= 3:
        hints.append(dict(id="scramble", icon="🧩", label="철자 섞기",
                          text="이 글자들을 바르게 배열해 보세요.", tiles=scramble(answer)))
    if n >= 4:
        shown = math.ceil(n / 2)
        hints.append(dict(id="half", icon="👀", label="절반 공개",
                          text=f"앞의 {shown}글자를 빈칸에 보여 줄게요."))
    return hints


def make_blank(w, is_original):
    """Question + hints for one word (shown on the quiz screen)."""
    if is_original:
        # The 20 original items keep their own sentence, translation and grammar note.
        q = dict(w["quiz"], kind="sentence")
    else:
        forms = [w["word"], *w["variation"]]
        found = find_in_sentence(w["ex"], forms)
        if found:
            pattern = re.compile(r"(?<![A-Za-z])" + re.escape(found) + r"(?![A-Za-z])")
            answers = [found] + [f for f in forms if f.lower() != found.lower()]
            q = dict(s=pattern.sub("___", w["ex"], count=1), tr=f"뜻: {w['meaning']}",
                     a=answers, kind="sentence",
                     note="예문 속 쓰임과 철자를 함께 기억해 보세요.")
        else:
            # No example sentence: write the word from its meaning.
            q = dict(s="영어로 쓰세요: ___", tr=w["meaning"], a=forms, kind="meaning",
                     note="기본형 철자를 확인해 보세요.")
    q["hints"] = make_hints(w, q["a"][0], is_original)
    return q


@st.cache_data
def build_page():
    words = load_library()
    original = read_json("original_words.json", [])
    audio = read_json("audio.json", {})

    # Same rule as the app: original items overwrite the list, but level/meaning stay from the list.
    original_by_word = {o["word"].lower(): o for o in original}
    merged = []
    for w in words:
        old = original_by_word.get(w["word"].lower())
        if old:
            w = {**w, **old, "level": w["level"], "meaning": w["meaning"], "variation": w["variation"]}
        w["blank"] = make_blank(w, old is not None)
        merged.append(w)

    def js(data):
        # "</" is escaped so the data can never close the <script> tag early.
        return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    html = (BASE / "daily_words.html").read_text(encoding="utf-8")
    html = html.replace("/*__AUDIO_JSON__*/{}", js(audio))
    html = html.replace("/*__ORIGINAL_WORDS_JSON__*/[]", js(original))
    html = html.replace("/*__WORDS_JSON__*/[]", js(merged))
    return html


components.html(build_page(), height=APP_HEIGHT, scrolling=False)
