from tempfile import SpooledTemporaryFile

def get_valid_ips() -> list[str]:
    with open("src/valid_ips.txt", "r") as archivo:
        contenido = archivo.read()
        lineas = contenido.split("\n")

    return lineas

def return_streaming_audio(audio_file):
    with SpooledTemporaryFile() as temp_file:
        temp_file.write(audio_file)
        temp_file.seek(0)
        yield from temp_file