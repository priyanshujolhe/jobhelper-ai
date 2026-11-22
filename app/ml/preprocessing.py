import re
import string

# Curated English stop words list (comprehensive, without external NLTK downloads requirement)
ENGLISH_STOP_WORDS = frozenset([
    "a", "about", "above", "across", "after", "afterwards", "again", "against", "all",
    "almost", "alone", "along", "already", "also", "although", "always", "am", "among",
    "amongst", "amoungst", "amount", "an", "and", "another", "any", "anyhow", "anyone",
    "anything", "anyway", "anywhere", "are", "around", "as", "at", "back", "be", "became",
    "because", "become", "becomes", "becoming", "been", "before", "beforehand", "behind",
    "being", "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom",
    "but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry",
    "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight",
    "either", "eleven", "else", "elsewhere", "empty", "enough", "etc", "even", "ever",
    "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fifty",
    "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found",
    "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt",
    "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers",
    "herself", "him", "himself", "his", "how", "however", "hundred", "i", "ie", "if", "in",
    "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter",
    "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might",
    "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my",
    "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no",
    "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off",
    "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our",
    "ours", "ourselves", "out", "over", "own", "part", "per", "perhaps", "please", "put",
    "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several",
    "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some",
    "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such",
    "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then",
    "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these",
    "they", "thick", "thin", "third", "this", "those", "though", "three", "through",
    "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards",
    "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very", "via",
    "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where",
    "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether",
    "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will",
    "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself",
    "yourselves"
])


def clean_text(text: str) -> str:
    """
    Normalizes text by removing HTML tags, non-printable characters,
    URLs, and normalizing whitespace.
    """
    if not text:
        return ""

    # Remove HTML tags
    cleaned = re.sub(r"<[^>]+>", " ", text)
    # Remove URLs
    cleaned = re.sub(r"https?://\S+|www\.\S+", " ", cleaned)
    # Remove email addresses from generic NLP text (keeps it neutral for matching)
    cleaned = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", " ", cleaned)
    # Normalize unicode quotes and dashes
    cleaned = (
        cleaned.replace("’", "'")
        .replace("‘", "'")
        .replace("“", '"')
        .replace("”", '"')
        .replace("–", "-")
        .replace("—", "-")
        .replace("•", " ")
    )
    # Remove non-ascii characters but keep common punctuation
    cleaned = re.sub(r"[^\x00-\x7F]+", " ", cleaned)
    # Normalize whitespaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def tokenize(text: str) -> list[str]:
    """
    Tokenizes text into word tokens while preserving programming tokens like C++, C#, .NET.
    """
    if not text:
        return []

    # Preserve special technical terms first: c++, c#, .net, node.js
    pattern = r"c\+\+|c\#|\.net|node\.js|\b[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*\b"
    tokens = re.findall(pattern, text.lower())
    return tokens


def remove_stopwords(tokens: list[str]) -> list[str]:
    """Removes standard English stopwords from token list."""
    return [t for t in tokens if t not in ENGLISH_STOP_WORDS and len(t) > 1]


def simple_lemmatize(word: str) -> str:
    """
    Lightweight rule-based suffix normalizer (stemmer/lemmatizer)
    that leaves technical terms intact.
    """
    if len(word) <= 3 or word in {"c++", "c#", ".net", "sql", "css", "aws"}:
        return word

    # Common plural / tense endings
    if word.endswith("sses"):
        return word[:-2]
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("ing") and len(word) > 5:
        return word[:-3]
    if word.endswith("ed") and len(word) > 4:
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word


def preprocess_text(text: str) -> str:
    """
    Full pipeline: clean -> tokenize -> remove stopwords -> lemmatize -> join into string.
    Suitable for TF-IDF feature extraction.
    """
    cleaned = clean_text(text)
    tokens = tokenize(cleaned)
    filtered = remove_stopwords(tokens)
    lemmatized = [simple_lemmatize(t) for t in filtered]
    return " ".join(lemmatized)
