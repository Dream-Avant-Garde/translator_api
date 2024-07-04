import wave
import contextlib

def print_wav_headers(filename):
    with contextlib.closing(wave.open(filename, 'rb')) as f:
        params = f.getparams()
        print("Number of channels:", params.nchannels)
        print("Sample width (bytes):", params.sampwidth * 8, 'bits')
        print("Frame rate (sampling frequency):", params.framerate)
        print("Number of frames:", params.nframes)
        print("Compression type:", params.comptype)
        print("Compression name:", params.compname)

# Ejemplo de uso
print_wav_headers('test/in_audios/testaudio48.wav')
