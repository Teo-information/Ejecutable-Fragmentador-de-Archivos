import os
import math
import argparse
import subprocess
import time

def verificar_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except Exception:
        print("❌ ffmpeg no está instalado o no está en el PATH. Por favor, instálalo para usar este script.")
        return False

def archivo_valido(path):
    return os.path.isfile(path) and os.path.getsize(path) > 0

def guardar_segmento_ffmpeg(video_path, ruta_segmento, inicio, duracion, extension, intentos=3):
    for intento in range(1, intentos+1):
        try:
            # Construir comando ffmpeg
            cmd = [
                "ffmpeg", "-y", # overwrite output
                "-ss", str(inicio),
                "-t", str(duracion),
                "-i", video_path,
            ]
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

def fragmentar_video(video_path, duracion_segmento=300):
    if not archivo_valido(video_path):
        print(f"❌ El archivo {video_path} no existe o está vacío.")
        return

    nombre_archivo = os.path.basename(video_path)
    nombre_base, extension = os.path.splitext(nombre_archivo)
    carpeta_salida = os.path.join(os.path.dirname(video_path), nombre_base)
    os.makedirs(carpeta_salida, exist_ok=True)

    print(f"Procesando: {video_path}")
    try:
        # Obtener duración total con ffprobe
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path
        ]
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
            exito = guardar_segmento_ffmpeg(video_path, ruta_segmento, inicio, duracion_real, extension)
            if not exito:
                print(f"❌ No se pudo guardar el segmento {i+1} después de varios intentos.")
        print(f"✅ Fragmentación completa. Segmentos guardados en: {carpeta_salida}\n")
    except Exception as e:
        print(f"❌ Error procesando el archivo {video_path}: {e}")

def main():
    if not verificar_ffmpeg():
        return
    parser = argparse.ArgumentParser(description="Fragmentador de videos grandes por comando (usando ffmpeg).")
    parser.add_argument('--input', '-i', nargs='+', required=True, help='Ruta(s) de los videos a fragmentar')
    parser.add_argument('--segmento', '-s', type=int, default=5, help='Duración de cada segmento en minutos (por defecto 5)')
    args = parser.parse_args()

    duracion_segmento = args.segmento * 60
    for video_path in args.input:
        fragmentar_video(video_path, duracion_segmento)

if __name__ == "__main__":
    main() 