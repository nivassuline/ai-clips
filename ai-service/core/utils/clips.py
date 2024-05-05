from clipsai import ClipFinder, AudioVideoFile
from core.utils.common import extract_text_within_timestamp_range, extract_words_within_timestamp_range

def find_clips(transcript_method, duration_choice):
        # 0.  < 60 seconds
    # 1. 1 min - 3 min
    # 2. 3min - 10 min
    # 3. 10 min - 15min
    if duration_choice == 0:
        clipfinder = ClipFinder(max_clip_duration=60)
    if duration_choice == 1:
        clipfinder = ClipFinder(min_clip_duration=60, max_clip_duration=180)
    if duration_choice == 2:
        clipfinder = ClipFinder(min_clip_duration=180, max_clip_duration=600)
    if duration_choice == 3:
        clipfinder = ClipFinder(min_clip_duration=600, max_clip_duration=900)
    clips = clipfinder.find_clips(transcription=transcript_method)

    return clips

def trim_clips(clips, full_video_path,transcript_string, media_editor, words, upload_id):
    clips_array = []
    media_file = AudioVideoFile(full_video_path)
    for idx, clip in enumerate(clips):
        clips_obj = None
        duration = clip.end_time - clip.start_time
        filename = f"{idx}_trim_{upload_id}.mp4"

        media_editor.trim(
            media_file=media_file,
            start_time=clip.start_time,
            end_time=clip.end_time,
            trimmed_media_file_path=f"tmp/{filename}",
        )

        clips_obj = {
                    "path": f"tmp/{filename}",
                    "filename" : filename,
                    "duration": duration,
                    "transcript": extract_text_within_timestamp_range(clip.start_time, clip.end_time, transcript_string),
                    "words" : extract_words_within_timestamp_range(duration, words, clip.start_time)
                }  
        
        if clips_obj:
            clips_array.append(clips_obj) 

    return clips_array
    
