import bisect

import srt  # type: ignore


class VideoSubtitles:
    def __init__(self, srt_path):
        self.srt_path = srt_path
        self.parser = srt.parse(open(srt_path, "r").read())
        self.min_times = []
        self.max_times = []
        self.texts = []
        self._parse_subtitles()

    def _parse_subtitles(self):
        for p in self.parser:
            self.min_times.append(p.start.total_seconds())
            self.max_times.append(p.end.total_seconds())
            self.texts.append(p.content)

    def find_subtitle(self, time):
        idx = bisect.bisect_left(self.max_times, time)
        if (
            idx < len(self.max_times)
            and self.min_times[idx] <= time <= self.max_times[idx]
        ):
            return " ".join(self.texts[idx : idx + 2])
        else:
            return None
