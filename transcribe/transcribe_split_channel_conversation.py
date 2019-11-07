#-*- coding: utf-8 -*-
__author__ = "Chirag Rathod (Srce Cde)"
__license__ = "MIT"
__email__ = "chiragr83@gmail.com"
__maintainer__ = "Chirag Rathod (Srce Cde)"

import json
with open("channel-aws-audio.json", "r") as f:
    json_load = json.load(f)

channels = json_load["results"]["channel_labels"]
items = json_load["results"]["items"]

speaker_text = []
flag = False


for seg in channels["channels"]:
    for word in items:
        if "start_time" in word:
            if seg["items"]:
                for seg_item in seg["items"]:
                    if "start_time" in seg_item:
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
            f.write("{} : ".format(seg["channel_label"])+' '.join(speaker_text))
            f.write("\n")
    speaker_text = []
