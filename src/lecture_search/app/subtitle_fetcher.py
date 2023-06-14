import bisect

import srt  # type: ignore


def parse_subtitles(srt_path):
    parser = srt.parse(open(srt_path, "r").read())
    min_times = []
    max_times = []
    texts = []
    for p in parser:
        min_times.append(p.start.total_seconds())
        max_times.append(p.end.total_seconds())
        texts.append(p.content)
    return min_times, max_times, texts


def find_subtitle(min_times, max_times, texts, time, future=2):
    idx = bisect.bisect_left(max_times, time)
    if idx < len(max_times) and min_times[idx] <= time <= max_times[idx]:
        return texts[idx : idx + future]
    else:
        return None
