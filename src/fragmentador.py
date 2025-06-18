import os
import math
import subprocess
import time
import sys
import tempfile
import shutil
import urllib.request
import zipfile

def descargar_ffmpeg_win(destino):
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    zip_path = os.path.join(destino, "ffmpeg.zip")
    print("Descargando ffmpeg portable...")
    urllib.request.urlretrieve(url, zip_path)
    print("Descomprimiendo ffmpeg...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(destino)
    # Buscar la carpeta bin
    for root, dirs, files in os.walk(destino):
        if 'ffmpeg.exe' in files:
            return root
    return None

def verificar_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return "ffmpeg"  # Está en el PATH
    except Exception:
        if sys.platform.startswith("win"):
            tempdir = os.path.join(tempfile.gettempdir(), "ffmpeg_portable")
            if not os.path.exists(tempdir):
                os.makedirs(tempdir, exist_ok=True)
            ffmpeg_bin = descargar_ffmpeg_win(tempdir)
            if ffmpeg_bin:
                print(f"Usando ffmpeg portable en: {ffmpeg_bin}")
                return os.path.join(ffmpeg_bin, "ffmpeg.exe")
            else:
                print("No se pudo descargar ffmpeg portable. Por favor, instálalo manualmente.")
                return None
        else:
            print("❌ ffmpeg no está instalado o no está en el PATH. Por favor, instálalo para usar este programa.")
            return None

def archivo_valido(path):
    return os.path.isfile(path) and os.path.getsize(path) > 0

def es_archivo_soportado(path):
    ext = os.path.splitext(path)[1].lower()
    return ext in [".mp3", ".mp4", ".avi", ".mov", ".mkv", ".wav"]

def guardar_segmento_ffmpeg(ffmpeg_cmd, video_path, ruta_segmento, inicio, duracion, extension, intentos=3):
    for intento in range(1, intentos+1):
        try:
            cmd = [ffmpeg_cmd, "-y", "-ss", str(inicio), "-t", str(duracion), "-i", video_path]
            if extension.lower() in [".mp4", ".avi", ".mov", ".mkv"]:
                cmd += ["-c:v", "copy", "-c:a", "copy", ruta_segmento]
            else:
                cmd += ["-acodec", "copy", ruta_segmento]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0 and os.path.exists(ruta_segmento) and os.path.getsize(ruta_segmento) > 0:
                return True
            else:
                print(f"❌ Error ffmpeg (intento {intento}): {result.stderr.decode('utf-8').splitlines()[-5:]}")
        except Exception as e:
            print(f"❌ Error al guardar el segmento (intento {intento}): {e}")
        if intento < intentos:
            print("Reintentando en 2 segundos...")
            time.sleep(2)
    return False

def fragmentar_video(ffmpeg_cmd, video_path, duracion_segmento=300):
    if not archivo_valido(video_path):
        print(f"❌ El archivo {video_path} no existe o está vacío.")
        return
    if not es_archivo_soportado(video_path):
        print(f"❌ Formato no soportado: {video_path}")
        return
    nombre_archivo = os.path.basename(video_path)
    nombre_base, extension = os.path.splitext(nombre_archivo)
    carpeta_salida = os.path.join(os.path.dirname(video_path), nombre_base)
    os.makedirs(carpeta_salida, exist_ok=True)
    print(f"Procesando: {video_path}")
    try:
        # Usar ffprobe desde la misma carpeta que ffmpeg si es portable
        ffprobe_cmd = "ffprobe"
        if ffmpeg_cmd != "ffmpeg":
            ffprobe_cmd = os.path.join(os.path.dirname(ffmpeg_cmd), "ffprobe.exe")
        cmd = [ffprobe_cmd, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        duracion = float(result.stdout.decode().strip())
        num_segmentos = math.ceil(duracion / duracion_segmento)
        for i in range(num_segmentos):
            inicio = i * duracion_segmento
            duracion_real = min(duracion_segmento, duracion - inicio)
            if extension.lower() in [".mp4", ".avi", ".mov", ".mkv"]:
                nombre_segmento = f"{nombre_base}_part_{i+1}.mp4"
            else:
                nombre_segmento = f"{nombre_base}_part_{i+1}.mp3"
            ruta_segmento = os.path.join(carpeta_salida, nombre_segmento)
            print(f"  Guardando segmento {i+1}/{num_segmentos}: {ruta_segmento}")
            exito = guardar_segmento_ffmpeg(ffmpeg_cmd, video_path, ruta_segmento, inicio, duracion_real, extension)
            if not exito:
                print(f"❌ No se pudo guardar el segmento {i+1} después de varios intentos.")
        print(f"\n✅ Fragmentación completa. Segmentos guardados en: {carpeta_salida}\n")
    except Exception as e:
        print(f"❌ Error procesando el archivo {video_path}: {e}")

def main():
    print("""
=== Fragmentador de Audios/Video ===
Pega la ruta completa del archivo grande (mp3, mp4, etc.) o de una carpeta y presiona Enter.
Escribe 'salir' para terminar el programa.
""")
    ffmpeg_cmd = verificar_ffmpeg()
    if not ffmpeg_cmd:
        print("No se pudo encontrar ni instalar ffmpeg. Saliendo...")
        return
    while True:
        ruta = input("Ruta de archivo o carpeta (o 'salir'): ").strip().strip('"')
        if ruta.lower() == 'salir':
            print("¡Hasta luego!")
            break
        if os.path.isdir(ruta):
            print(f"Procesando todos los archivos soportados en la carpeta: {ruta}\n")
            archivos = [os.path.join(ruta, f) for f in os.listdir(ruta) if es_archivo_soportado(f)]
            if not archivos:
                print("No se encontraron archivos soportados en la carpeta.")
            else:
                print(f"Se encontraron {len(archivos)} archivos para fragmentar.\n")
                while True:
                    print("¿Cuántos minutos debe durar cada fragmento? (máximo 15, por defecto 5): ", end="")
                    try:
                        minutos = int(input().strip())
                        if minutos > 15:
                            print("No se permite fragmentar a más de 15 minutos. Intenta con un valor menor o igual a 15.")
                            continue
                        if minutos < 2:
                            print("El valor debe ser al menos 1 minuto.")
                            continue
                        break
                    except:
                        minutos = 5
                        break
                for archivo in archivos:
                    fragmentar_video(ffmpeg_cmd, archivo, minutos * 60)
        elif archivo_valido(ruta):
            while True:
                print("¿Cuántos minutos debe durar cada fragmento? (máximo 15, por defecto 5): ", end="")
                try:
                    minutos = int(input().strip())
                    if minutos > 15:
                        print("No se permite fragmentar a más de 15 minutos. Intenta con un valor menor o igual a 15.")
                        continue
                    if minutos < 2:
                        print("El valor debe ser al menos 1 minuto.")
                        continue
                    break
                except:
                    minutos = 5
                    break
            fragmentar_video(ffmpeg_cmd, ruta, minutos * 60)
        else:
            print("La ruta no es válida, el archivo no existe o el formato no es soportado.")

if __name__ == "__main__":
    main() 