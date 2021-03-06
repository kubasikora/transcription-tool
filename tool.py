import argparse, time, os, io
import pandas as pd
from google.cloud import speech
from progress.bar import Bar

parser = argparse.ArgumentParser(description='Process audio files')
parser.add_argument('-i', '--input', default=".", metavar='path', type=str, help="Input path for audio files")
parser.add_argument('-o', '--output', default="./output.csv", metavar='filename', type=str, help="Output path for csv raport")
parser.add_argument('--simple-context', action="store_true", help="Use simplified context")
parser.add_argument('--full-context', action="store_true", help="Use full context")
args = parser.parse_args()


def convert_speech_to_text(client, filepath, context):
    """Open and send audio file to google speech-to-text
    service.

    Args:
        client: speech-to-text client 
        filepath: path to audio file that should be send to 
        google cloud speech-to-text service
        context: list of words that define context

    Returns:
        response from google cloud cloud speech-to-text service
    """

    # create audio object
    with io.open(filepath, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)
    
    # create configuration object
    recognition_config = { "language_code": "pl-PL", "model": "command_and_search" }
    if len(context) != 0:
        recognition_config["speech_contexts"] = [speech.SpeechContext(phrases=context)]
    if filepath.endswith(".wav"):
        recognition_config["encoding"] = speech.RecognitionConfig.AudioEncoding.LINEAR16
    else:
        recognition_config["audio_channel_count"] = 2
        recognition_config["enable_separate_recognition_per_channel"] = True
    config = speech.RecognitionConfig(**recognition_config)

    try:
        return client.recognize(config=config, audio=audio)
    except:
        return None


def transcript(cloud_response):
    """Get text transcription with the highest confidence 
    from the response from google cloud speech-to-text 
    service. 

    Args: 
        cloud_response: response from speech-to-text service
    
    Returns:
        (transcription, confidence): string value of transcription
        with corresponding confidence score
    """

    transcription = None
    confidence = 0.0
    try:
        for result in cloud_response.results:
            for alt in result.alternatives:
                if confidence < alt.confidence:
                    confidence = alt.confidence
                    transcription = alt.transcript
    except:
        pass
    return (transcription, confidence)


def collect_files(path, audio_files):
    """Walks over files tree and collects all audio files
    with *.flac or *.wav extension. Stores all found paths 
    to audio files in audio_files container, provided as argument

    Args:
        path: starting prefix of files tree
        audio_files: container for storing all paths to audio files
    """

    for entry in os.scandir(path):
        if entry.is_dir():
            collect_files(entry.path, audio_files)
        if entry.is_file() and (entry.path.endswith(".flac") or entry.path.endswith(".wav")):
            audio_files.append(entry.path)


def process_files(audio_files, context=[]):
    """Processes each found audio file. For each file, sends it to 
    google cloud speech-to-text service, looks for the best transcription
    and saves it as a record (dictionary) in results list

    Args:
        audio_files: list of paths to audio files

    Returns:
        results: list of dictionaries, where each records stores information
        about files: 
            - path - path to audio file
            - transciption - string value of recognized command
            - confidence - confidence returned by the service
    """

    results = []
    bar_limit = len(audio_files)
    client = speech.SpeechClient()
    with Bar('Processing:', max=bar_limit) as bar:
        for audio in audio_files:
            response = convert_speech_to_text(client, audio, context)
            (transcription, confidence) = transcript(response)
            results.append({
                "path": audio,
                "transcription": transcription,
                "confidence": confidence
            })
            bar.next()
    return results


def create_context_list(simple_context=False, full_context=False):
    """Creates list with words that could be recognized by speech-to-text 
    service

    Args:
        simple_context: generate simple list with common start of a voice command
        full_context: generate list with all available commands 

    Returns:
        context: list with expectable words, by default returns empty list
    """

    if full_context:
        return [ "Hej", "Rico", "przynie??", "herbat??", "potwierdzam", "przyjed??", "tu", "tutaj" ]
    if simple_context:
        return ["Hej", "Rico"]
    else:
        return []


if __name__ == "__main__":
    audio_files = []
    collect_files(args.input, audio_files)
    context = create_context_list(args.simple_context, args.full_context)
    results = process_files(audio_files, context)
    pd.DataFrame(results).to_csv(args.output)
