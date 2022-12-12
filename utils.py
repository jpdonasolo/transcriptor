def seconds_to_minutes_and_seconds(seconds):
    seconds = int(seconds)
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"

def read_transcript(transcript_path):
    with open(transcript_path, "r") as file:
        transcript = file.read()
    lines = transcript.split("\n")
    lines = [line.split(",", 2) for line in lines]
    return lines