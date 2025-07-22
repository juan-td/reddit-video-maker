import re


def split_on_punctuation(text, max_length=250):
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    sections = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_length:
            current += (" " if current else "") + sentence
        else:
            if current:
                sections.append(current)
            else:
                sections.append(sentence)
            current = sentence

    sections.append(current.strip()) if current else None

    return sections


def replace_abbreviations(text):
    text = text.replace("’", "'")
    text = re.sub(r"\ba ?i ?t ?a\b", "Am i the asshole", text, flags=re.IGNORECASE)
    text = re.sub(r"\bt ?i ?f ?u\b", "Today i messed up", text, flags=re.IGNORECASE)
    text = re.sub(r"\bah\b", "asshole", text, flags=re.IGNORECASE)
    text = text.replace("/", " slash ")
    # Add space between numbers and letters, but keep multi-digit numbers together
    text = re.sub(r"(\d+)([A-Za-z])", r"\1 \2", text)
    text = re.sub(r"([A-Za-z])(\d+)", r"\1 \2", text)
    # Remove space between number and single 's' word (e.g., "3 s" -> "3s")
    text = re.sub(r"(\d+)\s+s\b", r"\1s", text)
    # Add space between word and parenthesis if missing (e.g., "word(" -> "word (", ")word" -> ") word")
    text = re.sub(r"([A-Za-z])([\(\)])", r"\1 \2", text)
    text = re.sub(r"([\(\)])([A-Za-z])", r"\1 \2", text)

    return text


def clean_text(text):
    # Move 's after a number in parenthesis inside and remove apostrophe, e.g., (13)'s -> (13s)
    text = replace_abbreviations(text)

    # Move 's after a number in parenthesis inside and remove apostrophe, e.g., (13)'s -> (13s)
    text = re.sub(r"\((\d+)\)'?s\b", r"(\1s)", text)
    # Add spaces around parentheses if missing (e.g., "word(" -> "word (", ")word" -> ") word")
    text = re.sub(r"(?<! )([\(\)])(?! )", r" \1 ", text)
    # Replace multiple spaces with a single space
    text = re.sub(r"\s{2,}", " ", text)
    # Convert all words with 2 or more letters to lowercase
    text = re.sub(r"\b([A-Za-z]{2,})\b", lambda m: m.group(1).lower(), text)
    # Replace variations of "tl;dr" with "TLDR"
    text = re.sub(r"\btl.?dr\b", "TLDR", text, flags=re.IGNORECASE)

    return text


if __name__ == '__main__':
    text = "little sister(13)'s"
    print(replace_abbreviations(text))
    print(clean_text(text))