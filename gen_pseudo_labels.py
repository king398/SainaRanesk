import whisper

model = whisper.load_model('medium')

audio = whisper.load_audio('/home/mithil/PycharmProjects/SainaRanesk/data/chunked_data/220714_2111_1.mp3')
audio = whisper.pad_or_trim(audio, 16000)

mel = whisper.log_mel_spectrogram(audio).to(model.device)

options = whisper.DecodingOptions(suppress_blank=False)

transcript = whisper.decode(model, mel, options)
print(transcript)