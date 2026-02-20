import ffmpeg

def convert_ogg_to_wav(audio_data: bytes) -> bytes:
    """
    Конвертирует аудио из формата OGG (формат голосовых Telegram) в WAV 
    с помощью ffmpeg in-memory (через pipe).
    """
    try:
        # Запускаем процесс ffmpeg
        # input('pipe:0') - чтение из stdin
        # output('pipe:1') - запись в stdout
        # format='wav', acodec='pcm_s16le', ac=1, ar='16k' - стандартные настройки для STT
        process = (
            ffmpeg
            .input('pipe:0')
            .output('pipe:1', format='wav', acodec='pcm_s16le', ac=1, ar='16k')
            .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
        )
        
        # Передаем аудио данные в stdin и получаем результат из stdout
        out, err = process.communicate(input=audio_data)
        
        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg ошибка конвертации: {err.decode('utf-8')}")
            
        return out
        
    except ffmpeg.Error as e:
        raise RuntimeError(f"FFmpeg ошибка: {e.stderr.decode('utf-8')}")
