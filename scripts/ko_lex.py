# -*- coding: utf-8 -*-
"""Korean grammar glossary: particles, endings, suffixes, and POS labels.

Hand written for a Korean-learning app aimed at English speaking K-pop fans.
Keys are mecab-ko morpheme surfaces; values are short English explanations
written for someone who has never studied Korean grammar formally.

Glosses stay under about 60 characters so they fit a tap popup on a phone.
"""

# ── 조사 (particles) ──────────────────────────────────────────────────
PARTICLES = {
    # 주격
    "이": "subject marker (after a consonant)",
    "가": "subject marker (after a vowel)",
    "께서": "subject marker, honorific",
    # 목적격
    "을": "object marker (after a consonant)",
    "를": "object marker (after a vowel)",
    # 주제·대조
    "은": "topic marker: as for ... (after a consonant)",
    "는": "topic marker: as for ... (after a vowel)",
    # 관형격
    "의": "possessive: ...'s, of ...",
    # 부사격
    "에": "at, in, to (place or time)",
    "에서": "at, from, in (where an action happens)",
    "에게": "to (a person)",
    "한테": "to (a person), casual",
    "께": "to (a person), honorific",
    "에게서": "from (a person)",
    "한테서": "from (a person), casual",
    "로": "to, toward, by means of (after a vowel or ㄹ)",
    "으로": "to, toward, by means of (after a consonant)",
    "와": "and, with (after a vowel)",
    "과": "and, with (after a consonant)",
    "랑": "and, with, casual",
    "이랑": "and, with, casual (after a consonant)",
    "하고": "and, with, spoken",
    "보다": "than (comparison)",
    "처럼": "like, as if",
    "같이": "like, together with",
    "만큼": "as much as",
    "대로": "just as, according to",
    "라고": "quoting: (saying) that ...",
    "이라고": "quoting: (saying) that ...",
    "라는": "that is called, so called",
    "부터": "from, starting at",
    "까지": "until, up to, all the way to",
    "마다": "every, each",
    "조차": "even (not even)",
    "에다": "onto, in addition to",
    # 보조사
    "도": "too, also, even",
    "만": "only, just",
    "밖에": "nothing but, only (with a negative)",
    "뿐": "only, nothing but",
    "이나": "or, or something, as many as",
    "나": "or, or something",
    "든지": "whether, any of",
    "야": "emphasis, or calling someone by name",
    "이야": "emphasis: it is ... (casual)",
    "요": "politeness tag added to the end",
    "이란": "as for the thing called ...",
    "커녕": "let alone, far from",
    "마저": "even, on top of that",
    "치고": "for a ..., considering it is a ...",
}

# ── 어미 (verb and adjective endings) ─────────────────────────────────
ENDINGS = {
    # 연결어미
    "고": "and, and then (links two clauses)",
    "거나": "or",
    "지만": "but, although",
    "는데": "setting up background: ..., and so / but",
    "은데": "setting up background: ..., and so / but",
    "ㄴ데": "setting up background: ..., and so / but",
    "니까": "because, since",
    "으니까": "because, since",
    "어서": "because, and then",
    "아서": "because, and then",
    "여서": "because, and then",
    "면": "if, when",
    "으면": "if, when",
    "려고": "intending to, in order to",
    "으려고": "intending to, in order to",
    "러": "in order to (with go or come)",
    "면서": "while doing, at the same time",
    "으면서": "while doing, at the same time",
    "다가": "and then suddenly, in the middle of",
    "도록": "so that, until",
    "자": "as soon as",
    "자마자": "as soon as",
    "는지": "whether, wondering if",
    "든": "whether, either way",
    "길": "that it would (wishing)",
    "게": "makes it an adverb: ...ly, in a ... way",
    "듯": "as if, like",
    "듯이": "as if, like",
    "더라도": "even if",
    "아도": "even if, even though",
    "어도": "even if, even though",
    "야": "only if, have to",
    "라": "command form, or quoting a command",
    # 선어말어미
    "었": "past tense",
    "았": "past tense",
    "였": "past tense",
    "겠": "will, probably, I guess",
    "시": "honorific: shows respect for the subject",
    "더": "recalling something witnessed before",
    # 관형사형
    "ㄴ": "modifier: the ... that happened (past, verbs)",
    "은": "modifier: the ... that happened (past, verbs)",
    "는": "modifier: the ... that is happening now",
    "ㄹ": "modifier: the ... that will happen",
    "을": "modifier: the ... that will happen",
    "던": "modifier: the ... that used to be, looking back",
    # 종결어미
    "다": "plain dictionary ending, also used in writing and lyrics",
    "어": "casual ending (to a close friend)",
    "아": "casual ending (to a close friend)",
    "지": "isn't it, you know (seeking agreement)",
    "네": "realizing something right now: oh, it is ...",
    "구나": "realizing something: ah, so it is ...",
    "군": "realizing something: ah, so it is ...",
    "나": "wondering: I wonder if ...",
    "까": "shall we, I wonder (question)",
    "ㄹ까": "shall I, I wonder",
    "을까": "shall I, I wonder",
    "자": "let's",
    "어라": "command, casual",
    "아라": "command, casual",
    "니": "casual question ending",
    "래": "I hear that, or how about",
    "대": "I hear that ...",
    "잖아": "you know that ..., as you know",
    "거든": "the thing is, because",
    "는걸": "but it is ... (soft protest)",
    "ㄴ가": "I wonder if",
    "을래": "do you want to, I will",
    "ㄹ래": "do you want to, I will",
    "습니다": "formal polite statement ending",
    "ㅂ니다": "formal polite statement ending",
    "어요": "polite ending",
    "아요": "polite ending",
    "세요": "polite honorific ending",
    "ㅆ어": "past tense, casual",
}

# ── 접사 (prefixes and suffixes) ──────────────────────────────────────
SUFFIXES = {
    "들": "plural marker",
    "하": "turns a noun into a verb: to do ...",
    "되": "turns a noun into a passive verb: to become ...",
    "스럽": "turns a noun into an adjective: ...like",
    "답": "turns a noun into an adjective: befitting a ...",
    "적": "turns a noun into an adjective: ...ic, ...al",
    "님": "honorific added to a name or title",
    "씨": "polite tag after a name: Mr., Ms.",
    "쯤": "about, approximately",
    "짜리": "worth, of that size",
    "거리": "something to do with",
    "히": "makes it an adverb: ...ly",
    "이": "makes it an adverb or a noun",
}

# ── 보조용사 (auxiliary verbs) ────────────────────────────────────────
AUXILIARIES = {
    "싶": "want to (used after -고)",
    "있": "to be, to exist; or -고 있다 = be ...ing",
    "없": "to not exist, to not have",
    "않": "not (negation)",
    "말": "do not (prohibition)",
    "보": "try doing, or seems like",
    "주": "do something for someone",
    "버리": "do it completely, and it is gone",
    "가": "keep going, continue",
    "오": "have been doing up to now",
    "지": "becomes, gets (passive or change of state)",
    "놓": "do it and leave it done",
    "두": "do it in advance and leave it",
    "하": "to do",
    "되": "to become, to be allowed",
    "같": "to be like, to seem",
}

# ── mecab-ko 품사 → 영어 라벨 ─────────────────────────────────────────
POS_LABEL = {
    "NNG": "noun",
    "NNP": "proper noun",
    "NNB": "counter / bound noun",
    "NNBC": "counter",
    "NR": "number",
    "NP": "pronoun",
    "VV": "verb",
    "VA": "adjective",
    "VX": "auxiliary verb",
    "VCP": "to be (copula)",
    "VCN": "to not be",
    "MM": "determiner",
    "MAG": "adverb",
    "MAJ": "conjunctive adverb",
    "IC": "interjection",
    "JKS": "particle",
    "JKC": "particle",
    "JKG": "particle",
    "JKO": "particle",
    "JKB": "particle",
    "JKV": "particle",
    "JKQ": "particle",
    "JX": "particle",
    "JC": "particle",
    "EP": "tense / honorific",
    "EF": "sentence ending",
    "EC": "connective ending",
    "ETN": "nominalizer",
    "ETM": "modifier ending",
    "XPN": "prefix",
    "XSN": "suffix",
    "XSV": "verb suffix",
    "XSA": "adjective suffix",
    "XR": "root",
    "SF": "punctuation",
    "SE": "punctuation",
    "SS": "punctuation",
    "SP": "punctuation",
    "SO": "punctuation",
    "SL": "foreign word",
    "SH": "chinese character",
    "SN": "number",
    "UNKNOWN": "unknown",
    "NA": "unknown",
}

# 사전형을 만들 때 다(ㄹ 수 있음)를 붙여야 하는 품사
VERBAL = {"VV", "VA", "VX", "VCP", "VCN"}
# 내용어: 어휘 후보로 뽑을 품사
CONTENT = {"NNG", "NNP", "NP", "NR", "VV", "VA", "VX", "MM", "MAG", "MAJ", "IC", "XR", "SL"}
# 문법 형태소: 문법 해설로 붙일 품사
GRAMMAR = {
    "JKS", "JKC", "JKG", "JKO", "JKB", "JKV", "JKQ", "JX", "JC",
    "EP", "EF", "EC", "ETN", "ETM", "XPN", "XSN", "XSV", "XSA",
}


def gloss(surface, pos):
    """형태소 하나의 영어 해설. 못 찾으면 None."""
    if pos in ("JKS", "JKC", "JKG", "JKO", "JKB", "JKV", "JKQ", "JX", "JC"):
        return PARTICLES.get(surface)
    if pos in ("EP", "EF", "EC", "ETN", "ETM"):
        return ENDINGS.get(surface)
    if pos in ("XSN", "XSV", "XSA", "XPN"):
        return SUFFIXES.get(surface)
    if pos == "VX":
        return AUXILIARIES.get(surface)
    return None


def lemma(surface, pos):
    """사전형. 용언은 다를 붙이고, 나머지는 표면형 그대로."""
    if pos in VERBAL:
        return surface + "다"
    return surface
