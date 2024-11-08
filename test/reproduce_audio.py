import soundfile as sf
import pyaudio

# Ruta del archivo WAV
file_path = "test\out_audios\out_audio.wav"

# Carga el archivo de audio con soundfile
data, sample_rate = sf.read(file_path, dtype='float32')
print(data[0:1024])
print(sample_rate)
# Inicializa PyAudio
p = pyaudio.PyAudio()

# Configura el stream de audio
stream = p.open(
    format=pyaudio.paFloat32,          # Formato de 32 bits en flotante
    channels=1,                        # Mono
    rate=sample_rate,                  # Frecuencia de muestreo (16000 Hz)
    output=True
)

# Reproduce el audio
stream.write(data.tobytes())

# Finaliza el stream
stream.stop_stream()
stream.close()
p.terminate()
