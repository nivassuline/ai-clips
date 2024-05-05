import os
import moviepy.editor as mpe
from moviepy.video.fx import headblur
from core.contents.face_cropping import crop_video
from core.utils.common import generate_random_string
from core.utils.effects import apply_gaussian_blur
import time
from clipsai import AudioVideoFile, resize
from multiprocessing import Pool
import threading


def split_text_into_lines(data):

    MaxChars = 15
    #maxduration in seconds
    MaxDuration = 2.0
    #Split if nothing is spoken (gap) for these many seconds
    MaxGap = 1.5

    subtitles = []
    line = []
    line_duration = 0
    line_chars = 0


    for idx,word_data in enumerate(data):
        word = word_data["word"]
        start = word_data["start"]
        end = word_data["end"]

        line.append(word_data)
        line_duration += end - start
        
        temp = " ".join(item["word"] for item in line)
        

        # Check if adding a new word exceeds the maximum character count or duration
        new_line_chars = len(temp)

        duration_exceeded = line_duration > MaxDuration 
        chars_exceeded = new_line_chars > MaxChars 
        if idx>0:
          gap = word_data['start'] - data[idx-1]['end'] 
          # print (word,start,end,gap)
          maxgap_exceeded = gap > MaxGap
        else:
          maxgap_exceeded = False
        

        if duration_exceeded or chars_exceeded or maxgap_exceeded:
            if line:
                subtitle_line = {
                    "word": " ".join(item["word"] for item in line),
                    "start": line[0]["start"],
                    "end": line[-1]["end"],
                    "textcontents": line
                }
                subtitles.append(subtitle_line)
                line = []
                line_duration = 0
                line_chars = 0


    if line:
        subtitle_line = {
            "word": " ".join(item["word"] for item in line),
            "start": line[0]["start"],
            "end": line[-1]["end"],
            "textcontents": line
        }
        subtitles.append(subtitle_line)

    return subtitles

def create_caption(textJSON, framesize, font="Aharoni-Bold", fontsize=56, color='white', shadow_color='black', shadow_opacity=1, shadow_offset=(-6, -11)): 
                                                                                                                                #(x , y), 
                                                                                                                                # x: left = negative, right = positive,
    full_duration = textJSON['end'] - textJSON['start']

    word_clips = []
    xy_textclips_positions = []

    # Calculate total width of the sentence
    total_sentence_width = sum([mpe.TextClip(wordJSON['word'], font=font, font_size=fontsize).w for wordJSON in textJSON['textcontents']])

    # Calculate x-position for center alignment
    x_pos = (framesize[0] - total_sentence_width) / 2
    y_pos = 0
    y_buffer = framesize[1] - 500

    textcontents_reversed = textJSON['textcontents'][::-1]

    for wordJSON in textcontents_reversed:
        duration = wordJSON['end'] - wordJSON['start']
        word_clip = mpe.TextClip(f"{wordJSON['word']} ", font=font, font_size=fontsize, color=color, method='caption', align='center').with_start(
            textJSON['start']).with_duration(full_duration)

        word_width, word_height = word_clip.size

        # Store info of each word_clip created
        xy_textclips_positions.append({
            "x_pos": x_pos,
            "y_pos": y_pos + y_buffer,
            "width": word_width,
            "height": word_height,
            "word": wordJSON['word'],
            "start": wordJSON['start'],
            "end": wordJSON['end'],
            "duration": duration
        })



        # Create shadow effect
        shadow_clip = mpe.TextClip(f"{wordJSON['word']} ", font=font, font_size=fontsize, color=shadow_color, method='caption', align='center', stroke_width=12, stroke_color='black').with_start(
            textJSON['start']).with_duration(full_duration)
        shadow_clip = shadow_clip.with_position((x_pos + shadow_offset[0], y_pos + y_buffer + shadow_offset[1]))
        shadow_clip = shadow_clip.with_opacity(shadow_opacity)
        word_clips.append(shadow_clip)

        word_clip = word_clip.with_position((x_pos, y_pos + y_buffer))
        word_clips.append(word_clip)

        # Increment x-position for the next word
        x_pos += word_width

        # Add space between words
        x_pos += 10  # Adjust this value for the desired space between words

    for highlight_word in xy_textclips_positions:
        word_clip_highlight = mpe.TextClip(highlight_word['word'], font=font, font_size=fontsize, color='red', method='caption', align='center').with_start(
            highlight_word['start']).with_duration(highlight_word['duration'])
        word_clip_highlight = word_clip_highlight.with_position(
            (highlight_word['x_pos'], highlight_word['y_pos'] + 1))
        word_clips.append(word_clip_highlight)

    return word_clips



def resize_clip(path, access_token, media_editor):
    media_file = AudioVideoFile(path)

    crops = resize(
    video_file_path=path,
    pyannote_auth_token=access_token,
    aspect_ratio=(9, 16),
    device='cuda',
    min_segment_duration=1
    )

    cropped_file_path = f'tmp/crop_{path.split("/")[-1]}'

    media_editor.resize_video(
    original_video_file=media_file,
    resized_video_file_path=cropped_file_path,  # doesn't exist yet
    width=crops.crop_width,
    height=crops.crop_height,
    segments=crops.to_dict()["segments"],
    )

    return cropped_file_path


def process_clip(idx, clip_obj, access_token, media_editor, crop, paths):
    w, h = 720, 1280
    id = generate_random_string(16)
    tmp_audio = f"tmp/audio_{idx}_{id}.wav"
    output_file = f"out/no_crop_{idx}_{id}.mp4"
    blurred_file = apply_gaussian_blur(clip_obj["path"].split('/')[1])

    clip = mpe.VideoFileClip(clip_obj["path"], audio=True).resize(width=w).with_position(("center", "center"))
    blurred_clip = mpe.VideoFileClip(blurred_file, audio=False).resize(height=h).with_position(("center", "center"))

    audio = clip.audio
    audio.write_audiofile(tmp_audio)
    subtitles_points = clip_obj["words"]
    linelevel_subtitles = split_text_into_lines(subtitles_points)

    subtitles = []
    for line in linelevel_subtitles:
        out = create_caption(line, (720, 1280))
        subtitles.extend(out)

    final = mpe.CompositeVideoClip([blurred_clip, clip] + subtitles, (w, h))
    final.write_videofile(output_file)

    if crop:
        cropped_output_file = f"out/crop_{id}.mp4"
        cropped_file_path = resize_clip(clip_obj["path"], access_token, media_editor)
        cropped_clip = mpe.VideoFileClip(cropped_file_path, audio=True).resize(width=w, height=h)
        final_cropped = mpe.CompositeVideoClip([cropped_clip] + subtitles, (w, h))
        final_cropped.write_videofile(cropped_output_file)
        cropped_clip.close()
        final_cropped.close()
        time.sleep(1.5)
        os.remove(cropped_file_path)

    os.remove(tmp_audio)
    os.remove(blurred_file)
    os.remove(clip_obj["path"])
    paths.append(output_file)

    print(f"Loop {idx} completed.")

def build_reel_format_videos(clips: list, access_token: str, media_editor, crop: bool = True) -> list[str]:
    paths = []

    print("Start building process...")
    func_start_time = time.time()

    threads = []
    for idx, clip_obj in enumerate(clips):
        thread = threading.Thread(target=process_clip, args=(idx, clip_obj, access_token, media_editor, crop, paths))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print(f"Function completed in {time.time() - func_start_time} seconds.")
    return paths
