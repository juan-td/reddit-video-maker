import re

abbreviation_dict = {
    "AITA": "Am I the Asshole",
    "WIBTA" : "Would I be the Asshole",
    "TIFU": "Today I messed up",
    "ELI5": "Explain Like I'm Five",
    "NSFW": "Not Safe For Work",
    "NSFL": "Not Safe For Life",
    "IMO": "In My Opinion",
    "IMHO": "In My Humble Opinion",
    "TLDR": "Too Long; Didn't Read",
    "AMA": "Ask Me Anything",
    "IIRC": "If I Recall Correctly",
    "IDK": "I Don't Know",
    "IRL": "In Real Life",
    "LPT": "Life Pro Tip",
    "DAE": "Does Anyone Else",
    "CMV": "Change My View",
    "SMH": "Shaking My Head",
    "TIL": "Today I Learned",
    "YMMV": "Your Mileage May Vary",
    "BRB": "Be Right Back",
    "LOL": "Laugh Out Loud",
    "ROFL": "Rolling On the Floor Laughing",
    "ICYMI": "In Case You Missed It",
    "FTFY": "Fixed That For You",
    "AFAIK": "As Far As I Know",
    "AAMOF": "As A Matter Of Fact",
    "BUMP": "Bring Up My Post",
    "MFW": "My Face When",
    "MRW": "My Reaction When",
    "ITT": "In This Thread",
    "TBT": "Throwback Thursday",
    "SFW": "Safe For Work",
    "IAMA": "I Am A",
    "RTFM": "Read The Fucking Manual",
    "NPC": "Non-Player Character",
    "DM": "Direct Message",
    "SIL": "Sister in Law",
    "BIL": "Brother in Law"
}

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
    for k,v in abbreviation_dict.items():
        abv = r"\b" + r" ?".join(list(k)) + r"\b"
        text = re.sub(abv, v, text, flags=re.IGNORECASE)
    text = re.sub(r"\bAH\b", "asshole", text)
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