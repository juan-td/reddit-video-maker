import os
import random
import shutil

from utils.audioGenerator import soundifyAuthor, soundifyComment, soundifyPost

from utils.redditScrape import scrapeComments, scrapeText
from utils.videoCreate import createVideo

from utils.textUtils import replace_abbreviations, clean_text, split_on_punctuation
import sys
import ollama
import json

subreddit = None
count = 1
span = "day"
lang_code = "en"
voice_samples_dir = "assets/voice_samples"
voice_files = [
    os.path.join(voice_samples_dir, f)
    for f in os.listdir(voice_samples_dir)
    if f.endswith(".mp3")
]

if len(sys.argv) > 1:
    video_type = "url"
    url = sys.argv[1]
else:
    video_type = input("enter video type (lf/ar/url/auto): ")
    if video_type == "url":
        url = input("enter video url: ")
    else:
        count = int(input("enter video count (1-10): "))
        span = input("enter time range (day/week/month): ")


def add_video_info(subreddit, author, post_id, title, transcript, video_path):
    video_info_path = os.path.join("exports", "video_info.json")
    os.makedirs("exports", exist_ok=True)

    # Load existing data or create new list
    if os.path.exists(video_info_path):
        with open(video_info_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Add new record
    data.append(
        {
            "subreddit" : subreddit,
            "author": author,
            "post_id": post_id,
            "title": title,
            "transcript": transcript,
            "video_path": video_path,
        }
    )

    # Save back to file
    with open(video_info_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def long_form():
    if video_type == "url":
        posts = scrapeText(subreddit, count, span, video_type=video_type, url=url)
    else:
        posts = scrapeText(subreddit, count, span)

    for post in posts:
        # Ask Ollama to classify the gender of the author based on post[1]
        response = ollama.chat(
            model="qwen3:1.7b",
            messages=[
            {
                "role": "system",
                "content": (
                "You are a gender classifier for Reddit posts. "
                "Your job is to determine the gender of the author (the person telling the story) based ONLY on the text provided. "
                "Output a single letter: 'm' for man, 'f' for woman. "
                "If you are unsure, make your best guess based on the evidence in the text. "
                "Do NOT output anything except 'm' or 'f'.\n\n"
                "Look for clues such as:\n"
                "- Age/gender tags in the format (25M), (F21), (m25), (f21), etc. These usually refer to the author.\n"
                "- Phrases like 'I (25M)', 'My (F21) sister', 'As a woman...', 'As a guy...', etc.\n"
                "- If multiple people are mentioned, focus on the person telling the story (the author).\n"
                "- Ignore the gender of other people mentioned in the story.\n"
                "- If the gender is not explicitly stated, infer from context, but always output only 'm' or 'f'.\n"
                "Examples:\n"
                "Text: 'I (25M) went to the store.' Output: m\n"
                "Text: 'My (F21) sister said...' (but the author is not the sister) Output: m or f depending on author clues\n"
                "Text: 'As a woman, I feel...' Output: f\n"
                "Text: 'My boyfriend and I...' (author is likely a woman) Output: f\n"
                "Text: 'My girlfriend and I...' (author is likely a man) Output: m\n"
                "Text: 'I (30F) think...' Output: f\n"
                "Text: 'I (M28) think...' Output: m\n"
                "Text: 'I am a 22 year old male...' Output: m\n"
                "Text: 'I am a 19 year old female...' Output: f\n"
                "Text: 'Today I messed up, I, F, early 20s...' Output: f\n"
                "Text: 'No gender clues.' Output: m or f (best guess)\n"
                ),
            },
            {
                "role": "user",
                "content": (
                f"Determine the gender of the author (the person telling the story) as 'm' or 'f'.\n"
                f"Reddit post title: {post[0].title}\n"
                f"Reddit post body: {post[1]}"
                ),
            },
            ],
            think=True,
        )
        print(response["message"]["thinking"])
        gender = response["message"]["content"].strip().lower()
        print(f"Speaker is: {gender}")
        voice_files_gendered = [
            vf for vf in voice_files if vf.endswith(f"{gender}.mp3")
        ]
        speaker = (
            random.choice(voice_files_gendered)
            if voice_files_gendered
            else random.choice(voice_files)
        )

        print("Author: ", post[0].author)

        if post[0].author is None:
            author = "[deleted]"
        else:
            author = str(post[0].author)

        try:
            shutil.rmtree("temp/" + author)
        except OSError:
            pass

        os.makedirs("temp/" + author)

        print(post[0].title)
        text = post[1]

        if len(text) > 5000:
            print("[INFO]: length of post is too long")
            continue
        sections = split_on_punctuation(text, 400)
        sections = [replace_abbreviations(s) for s in sections]
        sections_cleaned = [clean_text(s) for s in sections]

        for section in range(len(sections_cleaned)):
            soundifyPost(
                sections_cleaned[section],
                speaker,
                1,
                section,
                author,
                lang_code,
                sections[section],
            )

        post[0].title_cleaned = clean_text(post[0].title)
        post[0].title = replace_abbreviations(post[0].title)
        soundifyAuthor(post[0].title_cleaned, speaker, author, lang_code, post[0].title)

        createVideo(author,subreddit)

        try:
            shutil.rmtree(author)
        except OSError:
            pass

        add_video_info(
            subreddit,
            author,
            post[0].id,
            post[0].title,
            text,
            f"exports/{subreddit}/{author}.mp4",
        )


def askreddit():
    subreddit = "askreddit"
    posts = scrapeComments("askreddit", count, span)

    for post in posts:
        if post == [None]:
            quit()

        print("Title: ", post[0].title)
        response = ollama.chat(
            model="qwen3:1.7b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a classifier. Output only a single word: true or false.\n"
                        "Given a question, reply 'true' if it is related to politics, is controversial, or is NSFW (not safe for work), "
                        "otherwise reply 'false'.\n"
                        "Examples:\n"
                        "Q: What are your thoughts on the current president? A: true\n"
                        "Q: Should marijuana be legalized? A: true\n"
                        "Q: What's your favorite color? A: false\n"
                        "Q: How do I fix my computer? A: false\n"
                        "Q: Is abortion morally acceptable? A: true\n"
                        "Q: What's the best way to cook pasta? A: false\n"
                        "Q: Have you ever sent nudes? A: true\n"
                        "Q: What is the capital of France? A: false\n"
                        "Q: Why do people hate immigrants? A: true\n"
                        "Q: What's your favorite movie? A: false\n"
                        "Q: What's the worst thing you caught someone doing (NSFW)? A: true\n"
                        "Classify the following question:\n"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"""
                Classify either true or false if it is related to politics, is controversial, or is NSFW (not safe for work)
                --QUESTION START--
                {post[0].title}\n
                --QUESTION END--
                """
                    ),
                },
            ],
            think=True,
        )

        print(response["message"]["content"])
        political = response["message"]["content"].strip().lower()
        if political == "true":
            continue

        asker = str(post[0].author)

        if os.path.isdir("temp/" + asker):
            shutil.rmtree("temp/" + asker)

        subreddit = str(post[0].subreddit)

        os.makedirs("temp/" + asker)

        speaker = random.choice(voice_files)

        post[0].title_cleaned = clean_text(post[0].title)
        post[0].title = replace_abbreviations(post[0].title)
        soundifyAuthor(post[0].title_cleaned, speaker, asker, lang_code, post[0].title)

        post = [p for p in post if not hasattr(p, "body") or "[deleted]" not in p.body]

        for j in range(min(len(post), 8)):
            if j == 0:
                print("Title: ", post[j].title)
            else:
                prev_speaker = locals().get("speaker", None)
                available_speakers = [s for s in voice_files if s != prev_speaker]
                speaker = (
                    random.choice(available_speakers)
                    if available_speakers
                    else random.choice(voice_files)
                )

                text = f"{j}) " + post[j].body
                sections = split_on_punctuation(text, 400)
                sections = [replace_abbreviations(s) for s in sections]
                sections_cleaned = [clean_text(s) for s in sections]

                for section in range(len(sections_cleaned)):
                    soundifyComment(
                        sections_cleaned[section],
                        speaker,
                        j,
                        section,
                        asker,
                        "en",
                        sections[section],
                    )

        prev_speaker = locals().get("speaker", None)
        available_speakers = [s for s in voice_files if s != prev_speaker]

        createVideo(asker,subreddit)
        add_video_info(
            subreddit,
            asker,
            post[0].id,
            post[0].title,
            "\n\n".join([f"{k}) " + post[k].body for k in range(1, len(post))]),
            f"exports/{subreddit}/{asker}.mp4",
        )


match video_type:
    case "url":
        long_form()
    case "lf":
        subreddit = input("what subreddit: ")
        lang_code = input("enter language code (en/es): ")
        long_form()
    case "ar":
        askreddit()
    case "auto":
        for sub in ["amitheasshole", "tifu", "trueoffmychest"]:
            subreddit = sub
            long_form()
        askreddit()
