# Gestor de NFO para Cursos | Course NFO Manager

<div align="center">

[English](README_EN.md) | [简体中文](README.md) | [繁體中文](README_ZH_TW.md) | [日本語](README_JA.md) | [Español](README_ES.md) | [Deutsch](README_DE.md)

[![License](https://img.shields.io/github/license/your-username/course-nfo-manager)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/)
[![GitHub stars](https://img.shields.io/github/stars/your-username/course-nfo-manager)](https://github.com/your-username/course-nfo-manager/stargazers)

</div>

## 📖 Introducción al Proyecto

El Gestor de NFO para Cursos es una herramienta potente diseñada específicamente para gestionar y generar archivos NFO para cursos en línea. Ayuda a organizar y gestionar tu biblioteca de medios de cursos, resolviendo el problema del orden caótico de cursos generados automáticamente en bibliotecas de medios regulares.

### Características Principales

- 🚀 Soporte para generación y edición por lotes de archivos NFO
- 🖼️ Gestión inteligente de pósters de cursos
- 📁 Soporte para estructura de directorios multinivel
- 🏷️ Sistema inteligente de gestión de etiquetas
- 🔄 Herencia automática de etiquetas del directorio padre
- ⚡ Capacidades eficientes de procesamiento por lotes

### Compatibilidad

- ✅ Soporte completo para el Centro Multimedia NAS UGREEN
- 🌟 Teóricamente compatible con todo software de gestión de bibliotecas multimedia

## 🛠️ Requisitos Técnicos

- Python 3.6+
- Sistemas Operativos: Windows/Linux/macOS

## 📥 Guía de Instalación

### Método 1: Instalación usando pip (Recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/your-username/course-nfo-manager.git
cd course-nfo-manager

# 2. Crear y activar el entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

### Método 2: Descarga Directa

1. Descarga la última versión desde la página de [Releases](https://github.com/your-username/course-nfo-manager/releases)
2. Extrae los archivos
3. Ejecuta el archivo ejecutable

## 🚀 Inicio Rápido

```bash
# Ejecutar el programa
python main.py
```

## 📂 Especificación de Estructura de Directorios

Los directorios de cursos deben seguir esta estructura:

```
NombreCurso[IdentificadorIdioma]
├── MandarinDeepl/          # Directorio de cursos en chino
│   ├── Capítulo1/
│   │   ├── 1.1Lección.mp4
│   │   └── 1.2Lección.mp4
│   └── Capítulo2/
└── Original/               # Directorio de cursos en idioma original
```

### Ejemplo

```
Complete C# Masterclass[Mandarin]
├── MandarinDeepl
│   ├── 1 - Tu Primer Programa en C# y Vista General de Visual Studio
│   │   ├── 1 - Introducción.mp4
│   │   └── 2 - Lo que Quieres Lograr.mp4
│   └── 2 - Tipos de Datos y Variables
│       ├── 20 - Más Tipos de Datos y sus Límites.mp4
│       └── 22 - Tipos de Datos: Entero, Flotante y Doble.mp4
└── Original
```

## 💡 Características Detalladas

### 1. Generador de NFO
- Reconocimiento de estructura de directorios multinivel
- Análisis inteligente de estructura de capítulos
- Sistema de herencia automática de etiquetas
- Opciones flexibles de sobrescritura

### 2. Editor de NFO
- Edición de información por lotes
- Sistema de gestión de pósters
- Sistema de etiquetas personalizadas

## 📸 Vista Previa de la Interfaz

<div align="center">
  <img src="docs/1.png" alt="Interfaz Principal" width="600"/>
  <br/>
  <img src="docs/4.png" alt="Edición NFO" width="600"/>
  <br/>
  <img src="docs/5.png" alt="Procesamiento por Lotes" width="600"/>
  <br/>
  <img src="docs/6.png" alt="Interfaz de Configuración" width="600"/>
</div>

## ⚠️ Notas Importantes

1. Convención de Nombres de Directorios de Cursos:
   - Los cursos en chino deben colocarse en el directorio `MandarinDeepl`
   - Los cursos en idioma original deben colocarse en el directorio `Original`
   - Los archivos NFO añadirán automáticamente los sufijos de idioma correspondientes
   - Los nombres de los directorios de cursos deben incluir el nombre original y la traducción al chino (si está disponible)

2. Procesamiento de Archivos .nomedia:
   - Actualmente, la función de detección de .nomedia está desactivada
   - Los archivos NFO siempre se generarán en el directorio `Original`
   - No afectará al escaneo y reconocimiento normal de la biblioteca de medios

3. Recomendaciones para Nombres de Archivos:
   - Se recomienda usar números arábigos para la numeración de capítulos
   - Evitar caracteres especiales en los nombres de archivos
   - Mantener la consistencia en el formato de nombres

4. Notas de Compatibilidad del Sistema:
   - Los usuarios de Windows deben tener en cuenta las limitaciones de longitud de ruta
   - Los usuarios de Linux/macOS deben tener en cuenta la sensibilidad a mayúsculas/minúsculas
   - Se recomienda guardar todos los archivos con codificación UTF-8

## 🤝 Guía de Contribución

Damos la bienvenida a todas las formas de contribución, ya sean nuevas características, mejoras en la documentación o informes de errores. Por favor, sigue estos pasos:

1. Haz un fork del repositorio
2. Crea tu rama de características (`git checkout -b feature/CaracterísticaIncreíble`)
3. Confirma tus cambios (`git commit -m 'Añadir alguna CaracterísticaIncreíble'`)
4. Empuja a la rama (`git push origin feature/CaracterísticaIncreíble`)
5. Abre una Solicitud de Extracción

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles

## 🌟 Agradecimientos

¡Gracias a todos los desarrolladores que han contribuido a este proyecto!

## 📮 Contacto

Si tienes alguna pregunta o sugerencia, no dudes en contactarnos a través de:

- Crear un [Issue](https://github.com/your-username/course-nfo-manager/issues)
- Enviar un correo a: [airmusic@msn.com](mailto:airmusic@msn.com)

---

<div align="center">

Si este proyecto te ayuda, por favor considera darle una ⭐️

</div> 