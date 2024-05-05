import random
import string
import math

def generate_random_string(n: int) -> str:
    return "".join(random.choice(string.hexdigits) for i in range(n))

def check_negative(s):
    try:
        f = float(s)
        if (f < 0):
            return True
        # Otherwise return false
        return False
    except ValueError:
        return False

def calculate_splits(number, max_chunk=8100):
    return (number + max_chunk - 1) // max_chunk


def get_section_length(choice, content_chunk):
    sections = []
    for obj in content_chunk:
        print(f'OBJECT: {obj["duration"]}')
        duration = obj["duration"]
        if choice == 0:
            if 30 <= duration <= 600:
                sections.append(obj)
        elif choice == 1:
            if 25 <= duration <= 70:
                sections.append(obj)
        elif choice == 2:
            if 50 <= duration <= 110:
                sections.append(obj)
        elif choice == 3:
            if duration >= 80:
                sections.append(obj)
    print(f'SECTIONS {sections}')
    return sections


def extract_text_within_timestamp_range(start_timestamp, end_timestamp, transcript_text):
    transcript = transcript_text.split('\n')
    result = ""
    
    for line in transcript:
        if ':' in line and len(line) > 1:
            parts = line.split(':')
            timestamp = parts[1].strip().split('-')
            text = parts[0].split('-')
            start = math.floor(float(timestamp[0].strip()))
            end = math.floor(float(timestamp[1].strip()))
            
            if start >= math.floor(start_timestamp) and end <= math.floor(end_timestamp):
                result += f"{text[0]}: {float(timestamp[0].strip())} - {float(timestamp[1].strip())}\n"
    
    return result



def extract_words_within_timestamp_range(duration, words_list, clip_start_time):
    result = []

    for word_obj in words_list:
        start = word_obj['start']
        end = word_obj['end']

        adjusted_start_time = start - clip_start_time
        adjusted_end_time = end - clip_start_time


        if 0 <= adjusted_start_time <= duration:
            result.append({"word": word_obj['word'], "start": adjusted_start_time, "end": adjusted_end_time})


    return result

def get_random_clips(clips_list: list):
    chosen_indices = set()
    chosen_clips = []
    while len(chosen_clips) < 10:
        clip_index = random.randint(0, len(clips_list) - 1)
        if clip_index not in chosen_indices:
            chosen_indices.add(clip_index)
            chosen_clips.append(clips_list[clip_index])
    return [chosen_clips[0]]