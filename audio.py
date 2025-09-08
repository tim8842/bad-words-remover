# from pydub import AudioSegment

# def censor_audio_volume(
#     input_path: str,
#     output_path: str,
#     timestamps: list[dict],
#     gap_before: float = 0.0,  # сколько секунд добавить до начала слова
#     gap_after: float = 0.0,   # сколько секунд добавить после конца слова
#     reduction_db: float = -30  # на сколько дБ уменьшить громкость (отрицательное число)
# ):
#     audio = AudioSegment.from_file(input_path)
#     duration = len(audio) / 1000  # длительность аудио в секундах

#     # Сортируем по времени начала слова
#     timestamps = sorted(timestamps, key=lambda x: x['start'])

#     output_audio = AudioSegment.empty()
#     cursor = 0  # позиция в миллисекундах

#     for entry in timestamps:
#         start = max(0, (entry['start'] + gap_before) * 1000)  # в мс
#         end = min(duration * 1000, (entry['end'] + gap_after) * 1000)

#         start = int(start)
#         end = int(end)

#         # Добавляем сегмент до начала слова без изменений
#         if start > cursor:
#             output_audio += audio[cursor:start]

#         # Берём сегмент с матом и уменьшаем громкость
#         censored_segment = audio[start:end] + reduction_db
#         output_audio += censored_segment

#         cursor = end

#     # Добавляем остаток аудио после последнего слова
#     if cursor < len(audio):
#         output_audio += audio[cursor:]

#     # Сохраняем результат
#     output_audio.export(output_path, format=output_path.split('.')[-1])

from pydub import AudioSegment

def censor_audio_volume(
    input_path: str,
    output_path: str,
    timestamps: list[dict],
    gap_before_percent: float = -0.1,  # 10% до начала
    gap_after_percent: float = -0.1,   # 10% после конца
    reduction_db: float = -30
):
    audio = AudioSegment.from_file(input_path)
    audio_length = len(audio)  # в миллисекундах

    timestamps = sorted(timestamps, key=lambda x: x['start'])
    output_audio = AudioSegment.empty()
    cursor = 0  # миллисекунды

    for entry in timestamps:
        seg_start_ms = entry['start'] * 1000
        seg_end_ms = entry['end'] * 1000
        seg_length = seg_end_ms - seg_start_ms

        # Считаем смещения по процентам
        before_shift = seg_length * gap_before_percent
        after_shift = seg_length * gap_after_percent

        start = int(max(0, seg_start_ms - before_shift))
        end = int(min(audio_length, seg_end_ms + after_shift))

        # Добавляем неизменённый участок
        if start > cursor:
            output_audio += audio[cursor:start]

        # Уменьшаем громкость "плохого" участка
        censored_segment = audio[start:end] + reduction_db
        output_audio += censored_segment

        cursor = end

    # Добавляем оставшийся хвост
    if cursor < audio_length:
        output_audio += audio[cursor:]

    # Удалим метаданные и отключим лишние заголовки (особенно для MP3)
    format_ = output_path.split('.')[-1].lower()
    parameters = ["-write_xing", "0"] if format_ == "mp3" else []

    output_audio.export(output_path, format=format_, parameters=parameters)
