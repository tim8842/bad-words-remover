from faster_whisper import WhisperModel, BatchedInferencePipeline
import string
import re
from trie import *
from audio import *

def extract_clean_words_with_timestamps(audio_path: str, min_len: int = 3) -> list[dict]:
    trie = build_trie(bad_words)
    model = WhisperModel("large-v3", device="cuda")
    batched_model = BatchedInferencePipeline(model=model)

    segments, info = batched_model.transcribe(
        audio_path,
        batch_size=4,
        word_timestamps=True,
        language="ru",
        beam_size=5,
        best_of=5,
    )

    clean_words = []
    for segment in segments:
        for word in segment.words:
            print(word.word)
            cleaned = re.sub(r'[^a-zA-Zа-яА-ЯёЁ]', '', word.word.lower())
            cleaned = cleaned.replace('ё', 'е')
            if len(cleaned) >= min_len and end_bad_word(trie, cleaned) and (word.end - word.start) <= 2.5:
                clean_words.append({
                    'word': cleaned,
                    'start': round(word.start, 2),
                    'end': round(word.end, 2)
                })

    return clean_words
file_name = "маты.wav"
bad_words_timestamps = extract_clean_words_with_timestamps(file_name)
print(bad_words_timestamps)
print(f"количетсво матов {len(bad_words_timestamps)}")

censor_audio_volume(
    input_path=file_name,
    output_path="censored_"+file_name,
    timestamps=bad_words_timestamps,
    gap_before_percent=-0.2,   # 50 мс оставить перед словом (чтобы слышалась первая буква)
    gap_after_percent=-0.2,     # 100 мс оставить после слова (последняя буква)
    reduction_db=-76   # уменьшить громкость на 40 дБ (почти полное заглушение)
)
