# Fragmentador de Audio/Video

Este proyecto proporciona dos herramientas para fragmentar archivos de audio y video en segmentos más pequeños:

## Herramientas

### 1. Fragmentador Interactivo (`fragmentador.py`)
- Interfaz interactiva por línea de comandos
- Soporta procesamiento de archivos individuales o carpetas completas
- Descarga automática de ffmpeg portable si no está instalado
- Límite de 15 minutos por segmento
- Formatos soportados: mp3, mp4, avi, mov, mkv, wav

### 2. Fragmentador por Comando (`fragmentar_videos.py`)
- Interfaz por línea de comandos con argumentos
- Procesa múltiples archivos en una sola ejecución
- Requiere ffmpeg instalado en el sistema
- Formatos soportados: mp3, mp4, avi, mov, mkv

## Requisitos
- Python 3.x
- ffmpeg (se descarga automáticamente en el modo interactivo)

## Uso

### Fragmentador Interactivo
```bash
python fragmentador.py
```

### Fragmentador por Comando
```bash
python fragmentar_videos.py -i video1.mp4 video2.mp4 -s 5
```
- `-i` o `--input`: Archivo(s) a fragmentar
- `-s` o `--segmento`: Duración de cada segmento en minutos (por defecto: 5) 