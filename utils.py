import os

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
    lines = [[line[0], line[1], *line[2].rsplit(",", 1)] for line in lines]
    lines = [[int(line[0]), int(line[1]), line[2], bool(int(line[3]))] for line in lines]
    return lines

def save_transcript(transcript, transcript_path):
    folder, basename = os.path.split(transcript_path)
    basename_no_ext = os.path.splitext(basename)[0]

    with open(os.path.join(folder, basename_no_ext + "_modified.txt"), "w") as file:
        for line in transcript:
            file.write(f"{line[0]},{line[1]},{line[2]},{int(line[3])}\n")

def raise_for_invalid_path(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)