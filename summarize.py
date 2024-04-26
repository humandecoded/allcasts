import whisper
import requests
import json
import os
import argparse


#this script assumes you already have saved audio files somehere on your computer
#this script assumes you already have llama3 running on your computer via ollama
#this script takes as input a single audio file, transcribes and summarizes it

#function that takes a file path to an audio file and returns the transcription
def WhisperTranscribe(audio_file):
    transcription = whisper.load_model("small.en").transcribe(audio_file)
    return transcription["text"]

# function that takes a transcription and returns a summarized version of the text
def LlamaSummarize(text):
    #start with just first 2000 words of text
    if len(text.split()) > 2000:
        text = " ".join(text.split()[:2000])
    
    #set up the post request to the llama3 api
    url = "http://localhost:11434/api/generate"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "prompt": "This is the first 15 minutes of a podcast. Summarize in no more than two paragraphs wha the speaker is discussing:" + text,
        "stream": False,
        "model": "llama3:70b",
        "keep_alive": 0
    }
    
    #make the post request
    response = requests.post(url, headers=headers, data=json.dumps(data))
    # return the response text
    return json.loads(response.text)["response"]
    
def main():
    #use argparse to get the path to the audio files
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, required=True, help="file to summarize")
    args = parser.parse_args()

    #define the path to a folder of audio files
    audio_file_path = args.file
    if audio_file_path.endswith('/'):
        audio_file_path = audio_file_path[:-1]



    #transcribe the audio
    print(f"Transcribing {audio_file_path}")
    transcription = WhisperTranscribe(audio_file_path)
    #summarize the transcription
    print(f"Summarizing {audio_file_path}")
    summary = LlamaSummarize(transcription)
    print(summary + "\n")
    #save to a text file
    with open(f"{audio_file_path}.summary", "w") as f:
        f.write(summary)
    with open(f"{audio_file_path}.transcription", "w") as f:
        f.write(transcription)


if __name__ == '__main__':
	main()

    