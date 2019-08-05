#-*- coding: utf-8 -*-
__author__ = "Chirag Rathod (Srce Cde)"
__license__ = "MIT"
__email__ = "chiragr83@gmail.com"
__maintainer__ = "Chirag Rathod (Srce Cde)"

import json
with open("tag-aws-audio.json", "r") as f:
    json_load = json.load(f)

segments = json_load["results"]["speaker_labels"]
items = json_load["results"]["items"]

speaker_text = []
flag = False


for seg in segments["segments"]:
    for word in items:
        if "start_time" in word:
            if seg["items"]:
                for seg_item in seg["items"]:
                    if word["end_time"] == seg_item["end_time"] and word["start_time"] == seg_item["start_time"]:
                        speaker_text.append(word["alternatives"][0]["content"])
                        flag = True
        elif word["type"] == "punctuation":
            if flag and speaker_text:
                temp = speaker_text[-1]
                temp += word["alternatives"][0]["content"]
                speaker_text[-1] = temp
                flag = False

    with open("transcribe.txt", "a") as f:
        if speaker_text:
            f.write("{} : ".format(seg["speaker_label"])+' '.join(speaker_text))
            f.write("\n")
    speaker_text = []
