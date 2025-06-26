# Fragmentador de Audios/Video

## Descripción

**Fragmentador de Audios/Video** es una herramienta interactiva para Windows que permite dividir archivos de audio y video en fragmentos más pequeños de manera sencilla y eficiente. Soporta múltiples formatos populares y utiliza `ffmpeg` para realizar la fragmentación de manera rápida y sin pérdida de calidad.

---

## Características

- Fragmenta archivos de audio y video por duración (minutos).
- Soporta formatos: `.mp3`, `.mp4`, `.avi`, `.mov`, `.mkv`, `.wav`.
- Fragmentación por lote de carpetas completas.
- Barra de progreso y mensajes en colores para mejor experiencia.
- Historial de archivos procesados en la sesión.
- Descarga automática de ffmpeg portable si no está instalado.
- Interfaz de consola amigable, con soporte para arrastrar y soltar rutas.

---

## Requisitos

- **Python 3.8 o superior**
- **Sistema operativo:** Windows (recomendado)
- **Dependencias de Python:**
  - `colorama`
- **Dependencia externa:** [ffmpeg](https://ffmpeg.org/) (el programa lo descarga automáticamente si no está en el sistema)

---

## Instalación

1. **Clona este repositorio o descarga los archivos.**

2. **Instala las dependencias de Python:**
   ```powershell
   pip install colorama
   ```

3. **(Opcional) Instala PyInstaller si deseas generar el ejecutable:**
   ```powershell
   pip install pyinstaller
   ```

---

## Uso

### Ejecutar desde la consola

```powershell
python src/fragmentador.py
```

### Generar el ejecutable (.exe)

```powershell
pyinstaller --onefile --console src/fragmentador.py
```
El ejecutable se encontrará en la carpeta `dist`.

---

## Ejemplo de uso

1. **Fragmentar un archivo individual**
   - Selecciona la opción `1` en el menú.
   - Escribe o arrastra y suelta la ruta del archivo.
   - Ingresa la duración de los fragmentos en minutos (máximo 15, por defecto 10).

2. **Fragmentar todos los archivos de una carpeta**
   - Selecciona la opción `2` en el menú.
   - Escribe o arrastra y suelta la ruta de la carpeta.
   - Ingresa la duración de los fragmentos.

3. **Ver ayuda**
   - Selecciona la opción `3`.

4. **Salir**
   - Selecciona la opción `4`.  
   - Se mostrará el historial de archivos procesados en la sesión.

---

## Notas

- Si `ffmpeg` no está instalado, el programa descargará una versión portable automáticamente.
- Puedes arrastrar y soltar archivos o carpetas directamente en la consola para facilitar la selección de rutas.
- Los fragmentos se guardan en una subcarpeta con el nombre del archivo original.

---

## Créditos

Realizado por Agentes IA  
Inspirado en las mejores prácticas de desarrollo de Google y Microsoft.

---

## Licencia

Este proyecto se distribuye bajo la licencia MIT.

---