# Utaun Android

Adaptación experimental con interfaz gráfica Kivy del generador Utaun Android-CUI.

## Compilar sin PC
1. Hacé un fork de https://github.com/Siveweb/Utaun
2. Subí el contenido de esta carpeta a la raíz de tu fork (incluida `.github/workflows/android.yml`).
3. En GitHub, abrí **Actions** y habilitá los workflows si te lo pide.
4. Elegí **Android APK Build** > **Run workflow**.
5. Cuando termine, descargá el artefacto **Utaun-Android-debug-apk**.

## Uso
Elegí `oto.ini`, elegí la carpeta de WAV de consonantes, completá los datos y generá el ZIP.

## Limitaciones de esta primera versión
- Es un proyecto fuente para compilar, no una APK ya compilada.
- La selección de archivos usa el acceso de almacenamiento externo tradicional; puede requerir ajustes según Android y los permisos del dispositivo.
- NumPy debe compilar correctamente en el entorno Android de GitHub Actions; si falla, habrá que ajustar versiones/recetas.
- Esta versión todavía no incorpora el recorte opcional de iconos del script original.

Basado en Utaun de Siveweb: https://github.com/Siveweb/Utaun
No es una versión oficial ni está afiliada al autor original.
