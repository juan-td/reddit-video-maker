from moviepy import *
import os
import random
from forcealign import ForceAlign
import re
import num2words
import sys


def force_align(transcript_path, audio_path):
    with open(transcript_path) as f_input:
        transcript = f_input.read()

    transcript = re.sub(
        r"(\d+)",
        lambda x: num2words.num2words(int(x.group(0))).replace(" ", "-"),
        transcript,
    )

    align = ForceAlign(audio_file=audio_path, transcript=transcript)
    words = align.inference()

    return words


def createVideo(username, subreddit):
    audioClip = []
    imageClip = []
    textClip = []
    length = -0.5

    startTimes = [0]

    if os.path.exists(username + "/constructed.mp4"):
        os.remove(username + "/constructed.mp4")

    for files in sorted(os.listdir("temp/" + username + "")):
        if ".mp3" in files:
            audioClip.append(
                AudioFileClip("temp/" + username + "/" + files)
                .with_start(length + 0.5)
                .with_effects([afx.AudioNormalize()])
            )
            length += AudioFileClip("temp/" + username + "/" + files).duration + 0.5
            startTimes.append(length)

    i = 0
    for files in sorted(os.listdir("temp/" + username + "")):
        if ".txt" in files and "_raw" not in files:
            transcript_path = "temp/" + username + "/" + files
            transcript_path_raw = (
                transcript_path.split(".")[0]
                + "_raw"
                + "."
                + transcript_path.split(".")[1]
            )
            with open(transcript_path_raw) as f_input:
                transcript = f_input.read()
            split_transcript = transcript.split(" ")
            split_transcript = [
                word for word in split_transcript if re.search(r"\w", word)
            ]
            audio_path = transcript_path.replace(".txt", ".mp3")
            words = force_align(transcript_path, audio_path)

            # For debugging
            for w in range(min(len(words), len(split_transcript))):
                print(words[w].word, split_transcript[w])

            for k in range(len(words)):
                word_duration_end = (
                    words[k + 1].time_start
                    if k < (len(words) - 1)
                    else words[k].time_end
                )
                clip = TextClip(
                    font="assets/fonts/Gotham Bold.otf",
                    text=split_transcript[k].upper(),
                    font_size=50,
                    margin=(70, 70),
                    color="white",
                    bg_color=None,
                    stroke_color="black",
                    stroke_width=8,
                    method="label",
                    text_align="center",
                    horizontal_align="center",
                    vertical_align="center",
                    interline=4,
                    transparent=True,
                    duration=word_duration_end - words[k].time_start,
                ).with_start(startTimes[i] + words[k].time_start)

                (w, h) = clip.size
                clip = clip.resized((w * 1.3, h * 1.3))
                (w, h) = (w * 1.3, h * 1.3)
                clip = clip.with_position((360 - w / 2, 640 - h / 2))

                textClip.append(clip)
            i += 1

        # if ".png" in files:
        #     clip = ImageClip("temp/"+username+"/"+files,duration=audioClip[i].duration).with_start(startTimes[i])

        #     (w,h) = clip.size
        #     clip = clip.resized((w*1.3,h*1.3))
        #     (w,h) = (w*1.3,h*1.3)
        #     clip = clip.with_position((360-w/2,640-h/2))
        #     clip = clip.with_opacity(0.9)
        #     imageClip.append(clip)
        #     i += 1

    videoAudio = CompositeAudioClip(audioClip)

    backgroundClip = ColorClip((720, 1280), (0, 0, 255), duration=videoAudio.duration)
    bg_files = [f for f in os.listdir("assets/bg_vids") if f.lower() != ".ds_store"]
    bg_file = bg_files[random.randrange(0, len(bg_files))]
    backgroundClip = VideoFileClip("assets/bg_vids/" + bg_file).resized((720, 1280))
    if int(backgroundClip.duration - videoAudio.duration) <= 0:
        repeats = int(videoAudio.duration / backgroundClip.duration) + 1
        repeated_clips = [backgroundClip] * repeats
        backgroundClip = concatenate_videoclips(repeated_clips, method="compose")
    videoStart = max(int(backgroundClip.duration - videoAudio.duration), 0)
    videoStart = random.randrange(0, videoStart)
    backgroundClip = backgroundClip.subclipped(
        videoStart, videoStart + videoAudio.duration
    )

    videoClip = backgroundClip
    # videoClip = CompositeVideoClip([videoClip] + imageClip)
    videoClip = CompositeVideoClip([videoClip] + textClip)
    music_files = [
        f
        for f in os.listdir("assets/music")
        if f.lower().endswith((".mp3", ".wav", ".ogg"))
    ]
    selected_music = music_files[random.randrange(0, len(music_files))]
    audio_background = AudioFileClip("assets/music/" + selected_music)
    if audio_background.duration < backgroundClip.duration:
        loops = int(backgroundClip.duration // audio_background.duration) + 1
        audio_background = concatenate_audioclips([audio_background] * loops)
    audio_background = audio_background.subclipped(0, backgroundClip.duration)
    audio_background = audio_background.with_effects([afx.MultiplyVolume(0.5)])
    final_audio = CompositeAudioClip([videoAudio, audio_background]).with_duration(
        backgroundClip.duration
    )
    videoClip.audio = final_audio
    # videoClip.write_videofile("exports/"+username+".webm", codec="libvpx-vp9", fps=24, preset="ultrafast", threads=4)
    
    export_dir = f"exports/{subreddit}"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    videoClip.write_videofile(f"{export_dir}/{username}.mp4", fps=30)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input("Username: ")
    createVideo(username,"unspecified")
