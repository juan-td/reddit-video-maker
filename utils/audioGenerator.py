# from TTS.api import TTS

# from kokoro import KPipeline
# import soundfile as sf

import torchaudio as ta
from chatterbox.tts import ChatterboxTTS


# def tts(text, speaker, filepath, language):
#     tts_obj = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to('mps')
#     tts_obj.tts_to_file(
#         text=text,
#         file_path=filepath,
#         speaker_wav=speaker,
#         language=language
#     )

# def tts(text, speaker, filepath, language):
#     pipeline = KPipeline(lang_code='a')
#     generator = pipeline(text, voice='af_heart')
#     for i, (gs, ps, audio) in enumerate(generator):
#         print(i, gs, ps)
#         sf.write(f'{filepath}', audio, 24000)

model = ChatterboxTTS.from_pretrained(device="mps")


def tts(text, speaker, filepath, language):
    wav = model.generate(text, audio_prompt_path=speaker)
    ta.save(filepath, wav, model.sr)


def soundifyAuthor(title, speaker, asker, lang_code, raw_title):
    tts(
        title,
        speaker,
        "temp/" + asker + "/temp" + "0" + ".mp3",
        lang_code,
    )

    with open("temp/" + asker + "/temp" + "0" + ".txt", "a") as f:
        f.write(title)

    with open(
        "temp/" + asker + "/temp" + "0" + "_raw" + ".txt", "a"
    ) as f:
        f.write(raw_title)


def soundifyComment(comment, speaker, index, sectionid, asker, lang_code, raw_comment):
    tts(
        comment,
        speaker,
        "temp/" + asker + "/temp" + str(index) + "_" + str(sectionid) + ".mp3",
        lang_code,
    )

    with open(
        "temp/" + asker + "/temp" + str(index) + "_" + str(sectionid) + ".txt", "a"
    ) as f:
        f.write(comment)

    with open(
        "temp/" + asker + "/temp" + str(index) + "_" + str(sectionid) + "_raw" + ".txt", "a"
    ) as f:
        f.write(raw_comment)


def soundifyPost(comment, speaker, index, sectionid, asker, lang_code, raw_comment):
    ## make numbers appear 01, 02, ... 09, 10, 11 to maintain order in directory
    if len(str(sectionid)) < 2:
        sectionid = "0" + str(sectionid)

    tts(
        comment,
        speaker,
        "temp/" + asker + "/temp" + str(index) + "_" + str(sectionid) + ".mp3",
        lang_code,
    )

    with open(
        "temp/" + asker + "/temp" + str(index) + "_" + str(sectionid) + ".txt", "a"
    ) as f:
        f.write(comment)

    with open(
        "temp/" + asker + "/temp" + str(index) + "_" + str(sectionid) + "_raw" + ".txt", "a"
    ) as f:
        f.write(raw_comment)
