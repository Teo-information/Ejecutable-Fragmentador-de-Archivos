import os
import math
import subprocess
import time
import sys
import tempfile
import shutil
import urllib.request
import zipfile
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

def descargar_ffmpeg_win(destino):
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    zip_path = os.path.join(destino, "ffmpeg.zip")
    # Si ya existe ffmpeg.exe en alguna subcarpeta, no descargar de nuevo
    for root, dirs, files in os.walk(destino):
        if 'ffmpeg.exe' in files:
            print(f"ffmpeg ya está descargado en: {root}")
            return root
    print("Descargando ffmpeg portable...")

    def mostrar_progreso(count, block_size, total_size):
        porcentaje = int(count * block_size * 100 / total_size)
        porcentaje = min(porcentaje, 100)
        barra = ('#' * (porcentaje // 2)).ljust(50)
        sys.stdout.write(f"\r[{barra}] {porcentaje}%")
        sys.stdout.flush()
        if porcentaje == 100:
            print()

    urllib.request.urlretrieve(url, zip_path, mostrar_progreso)
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
            # Si ya existe ffmpeg.exe, no descargar de nuevo
            for root, dirs, files in os.walk(tempdir):
                if 'ffmpeg.exe' in files:
                    print(f"Usando ffmpeg portable en: {root}")
                    return os.path.join(root, "ffmpeg.exe")
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
            print(Fore.RED + f"❌ Error al guardar el segmento (intento {intento}): {e}")
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
            
            # Barra de progreso
            porcentaje = int((i + 1) * 100 / num_segmentos)
            barra = ('#' * (porcentaje // 2)).ljust(50)
            print(f"\rFragmentando: [{barra}] {porcentaje}%  ({i+1}/{num_segmentos})", end='', flush=True)
            
            exito = guardar_segmento_ffmpeg(ffmpeg_cmd, video_path, ruta_segmento, inicio, duracion_real, extension)
            if not exito:
                print(f"\n{Fore.RED}❌ No se pudo guardar el segmento {i+1} después de varios intentos.")
        print(f"\r{Fore.GREEN}✅ Fragmentación completa. Segmentos guardados en: {carpeta_salida}\n")
    except Exception as e:
        print(f"❌ Error procesando el archivo {video_path}: {e}")

def mostrar_ayuda():
    print("""
=== Ayuda ===
1. Fragmentar archivo: Fragmenta un solo archivo de audio o video en partes más pequeñas.
2. Fragmentar carpeta: Fragmenta todos los archivos soportados dentro de una carpeta.
3. Salir: Cierra el programa.

Formatos soportados: mp3, mp4, avi, mov, mkv, wav.
Por defecto, cada fragmento dura 10 minutos (puedes cambiarlo).

Realizado por Agentes IA
""")

def menu_principal():
    print("""
=== Fragmentador de Audios/Video ===
Selecciona una opción:
1. Fragmentar archivo
2. Fragmentar carpeta
3. Ayuda
4. Salir
""")

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    ffmpeg_cmd = verificar_ffmpeg()
    if not ffmpeg_cmd:
        print(Fore.RED + "No se pudo encontrar ni instalar ffmpeg. Saliendo...")
        return
    historial = []  # Historial de archivos procesados
    while True:
        menu_principal()
        opcion = input("Opción (1-4): ").strip()
        if opcion == "1":
            limpiar_pantalla()
            print(Fore.CYAN + "=== Fragmentar archivo ===")
            print("Puedes escribir o ARRÁSTRAR Y SOLTAR aquí el archivo de audio o video que deseas fragmentar.")
            ruta = input("Ruta del archivo a fragmentar: ").strip().strip('"')
            if not archivo_valido(ruta):
                print(Fore.RED + "❌ La ruta no es válida, el archivo no existe o el formato no es soportado. Intenta nuevamente.")
                continue
            while True:
                minutos_str = input("¿Cuántos minutos debe durar cada fragmento? (máximo 15, por defecto 10): ").strip()
                if minutos_str == "":
                    minutos = 10
                    break
                try:
                    minutos = int(minutos_str)
                    if minutos > 15:
                        print(Fore.YELLOW + "⚠️ No se permite fragmentar a más de 15 minutos. Intenta con un valor menor o igual a 15.")
                        continue
                    if minutos < 1:
                        print(Fore.YELLOW + "⚠️ El valor debe ser al menos 1 minuto.")
                        continue
                    break
                except:
                    print(Fore.YELLOW + "⚠️ Valor inválido. Por favor, ingresa solo números.")
            print(Fore.CYAN + f"Iniciando fragmentación de '{os.path.basename(ruta)}' en fragmentos de {minutos} minutos...")
            fragmentar_video(ffmpeg_cmd, ruta, minutos * 60)
            historial.append(ruta)
        elif opcion == "2":
            limpiar_pantalla()
            print(Fore.CYAN + "=== Fragmentar carpeta ===")
            print("Puedes escribir o ARRÁSTRAR Y SOLTAR aquí la carpeta que contiene los archivos a fragmentar.")
            ruta = input("Ruta de la carpeta a fragmentar: ").strip().strip('"')
            if not os.path.isdir(ruta):
                print(Fore.RED + "❌ La ruta no es una carpeta válida. Intenta nuevamente.")
                continue
            archivos = [os.path.join(ruta, f) for f in os.listdir(ruta) if es_archivo_soportado(f)]
            if not archivos:
                print(Fore.YELLOW + "⚠️ No se encontraron archivos soportados en la carpeta.")
                continue
            print(Fore.CYAN + f"Se encontraron {len(archivos)} archivos para fragmentar.\n")
            while True:
                minutos_str = input("¿Cuántos minutos debe durar cada fragmento? (máximo 15, por defecto 10): ").strip()
                if minutos_str == "":
                    minutos = 10
                    break
                try:
                    minutos = int(minutos_str)
                    if minutos > 15:
                        print(Fore.YELLOW + "⚠️ No se permite fragmentar a más de 15 minutos. Intenta con un valor menor o igual a 15.")
                        continue
                    if minutos < 1:
                        print(Fore.YELLOW + "⚠️ El valor debe ser al menos 1 minuto.")
                        continue
                    break
                except:
                    print(Fore.YELLOW + "⚠️ Valor inválido. Por favor, ingresa solo números.")
            print(Fore.CYAN + f"Iniciando fragmentación de {len(archivos)} archivos en fragmentos de {minutos} minutos...")
            for archivo in archivos:
                fragmentar_video(ffmpeg_cmd, archivo, minutos * 60)
                historial.append(archivo)
        elif opcion == "3":
            limpiar_pantalla()
            mostrar_ayuda()
        elif opcion == "4":
            print(Fore.GREEN + "¡Hasta luego! Gracias por usar el Fragmentador de Audios/Video.")
            if historial:
                print(Fore.CYAN + "\nArchivos procesados en esta sesión:")
                for idx, archivo in enumerate(historial, 1):
                    print(f"{idx}. {archivo}")
            break
        else:
            limpiar_pantalla()
            print(Fore.YELLOW + "Opción no válida. Por favor, selecciona una opción del 1 al 4.")

if __name__ == "__main__":
    main()