import json
import time


response_obj='''
  {
    "hashtags": put here the list of hashtags in this format [#hashtag1, #hastag2] and so on,
    "explanation": put the explanation here of why the clip is viral / interesting,
    "viral score" : 87
  },
'''

def analyze_transcript(openai, clip_obj, language):

    # prompt = f"This is a transcript of a video. Please identify the most interesing sections from the whole, make sure that the duration is more than 2 minutes (it MUST to be more than 120 seconds, if its not more then 120 seconds don't use it), also make sure not to cut off any sections mid sentence its very (you MUST not cut sections off mid sentence), Make Sure you provide extremely accurate timestamps and respond only in this JSON format {response_obj}  \n Here is the Transcription:\n{transcript}"
    # prompt = f"This is a transcript of a video. Please identify the most interesing sections from the whole, make sure that the duration is {section_length_dict[index]} (it MUST to be {section_length_dict[index]} ,if its not {section_length_dict[index]} don't use it), make sure the sections start from a point that its easy to understand what the section is about, don't start the section mid sentence, Also its very importent the section doesn't end mid sentence or mid viral moment,Also give a viral score (viral score means how likely the most interesing section is to go viral) Make Sure you provide extremely accurate timestamps and respond only in this JSON format {response_obj}  \n Here is the Transcription:\n{transcript}"
    prompt = f"I will give you a transcript of a video. give a viral score (viral score means how likely the most interesing section is to go viral), and explain why its interesting or viral IN THIS LANGUAGE ONLY {language}, Also please provide short hastags related to the video content max 10 hashtags IN THIS LANGUAGE ONLY {language}, Make Sure you respond only in this JSON format {response_obj}  \n Here is the Transcription:\n{clip_obj['transcript']}"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=
    [       {"role": "system", "content": "Viral Context Extractor bot is a Video Maker with a lot of experience in this sector and help you by a transcript of a video return a JSON Array object with the informations of the most important parts, funniest and viral for social, and will give a score."},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": response_obj},
         ],
        n=1,
        stop=None
    )

    print(response.choices[0]['message'])

    return response.choices[0]['message']


def get_gpt_clips(openai, og_clips: list, language):
    clips = []
    for clip in og_clips:
        while True:
            clip_details = {}
            try:
                gpt_response = analyze_transcript(openai,clip,language)
                clip_details.update(json.loads(gpt_response["content"]))
                clip_details.update(clip)
                clips.append(clip_details)
                break  # If the operation succeeds, exit the while loop
            except openai.error.RateLimitError as e:
                print(f'Error: {e}')
                print("Rate limit exceeded. Retrying in 30 seconds...")
                time.sleep(30)
            except Exception as e:
                print(e)
                break
    return clips
