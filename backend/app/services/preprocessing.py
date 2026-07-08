import re
from functools import lru_cache

import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import PorterStemmer, WordNetLemmatizer
from rapidfuzz import process


nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)

STOP_WORDS = set(stopwords.words("english"))
STEMMER = PorterStemmer()
LEMMATIZER = WordNetLemmatizer()


class QueryProcessor:
    def __init__(self, vocabulary: list[str], alias_map: dict[str, str], symptom_map: dict[str, list[str]]):
        self.vocabulary = vocabulary
        self.alias_map = alias_map
        self.symptom_map = symptom_map

    @staticmethod
    def normalize_text(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text

    def tokenize(self, text: str) -> list[str]:
        return [token for token in self.normalize_text(text).split() if token and token not in STOP_WORDS]

    def lemmatize_and_stem(self, tokens: list[str]) -> list[str]:
        return [STEMMER.stem(LEMMATIZER.lemmatize(t)) for t in tokens]

    def spell_correct(self, query: str) -> str | None:
        best = process.extractOne(query, self.vocabulary, score_cutoff=70)
        if not best:
            return None
        return best[0] if best[0] != query else None

    @lru_cache(maxsize=4096)
    def expand_query(self, query: str) -> list[str]:
        normalized = self.normalize_text(query)
        terms = set(self.tokenize(normalized))

        if normalized in self.alias_map:
            terms.update(self.tokenize(self.alias_map[normalized]))

        for term in list(terms):
            if term in self.symptom_map:
                terms.update(self.tokenize(" ".join(self.symptom_map[term])))

            for syn in wordnet.synsets(term)[:3]:
                for lemma in syn.lemma_names()[:2]:
                    if lemma.isalpha() and len(lemma) > 2:
                        terms.add(lemma.lower().replace("_", " "))

        return sorted(terms)
