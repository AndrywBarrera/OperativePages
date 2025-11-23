# 🖥️ Simulador de Sistema Operativo

Simulador educativo de Sistema Operativo desarrollado en Python con interfaz gráfica moderna usando CustomTkinter. Permite visualizar y comprender los mecanismos fundamentales de planificación de procesos, gestión de memoria y sistema de archivos.

**Tecnologías:** Python 3.x | CustomTkinter | Threading  
**Proyecto académico:** UPTC - Sistemas Operativos 2025-2

## 📋 Características

### Planificación de Procesos
- **Round Robin (RR)**: Asignación cíclica con quantum configurable
- **Shortest Job First (SJF)**: Prioriza procesos con menor tiempo de ráfaga
- **Priority Scheduling**: Planificación basada en prioridades

### Gestión de Memoria
- Memoria virtual con paginación
- Algoritmos de reemplazo:
  - **FIFO** (First In First Out)
  - **LRU** (Least Recently Used)
- Visualización en tiempo real de frames de memoria

### Sistema de Archivos
- Control de concurrencia con locks
- Registro de accesos (exitosos y conflictos)
- Simulación de operaciones de lectura/escritura

## 🚀 Instalación

### Requisitos previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/os-simulator.git
cd os-simulator
```

2. **Instalar dependencias**
```bash
pip install customtkinter
```

3. **Ejecutar el simulador**
```bash
python main.py
```

> **Nota:** El simulador funciona sin CustomTkinter usando Tkinter estándar, pero la interfaz será menos moderna.

## 🎮 Uso

1. **Configurar parámetros:**
   - Seleccionar algoritmo de planificación (RR, SJF, PRIORITY)
   - Definir número de procesos a simular
   - Establecer quantum (para Round Robin)
   - Configurar frames de memoria disponibles

2. **Controles:**
   - ▶️ **INICIAR**: Comienza la simulación
   - ⏸️ **PAUSAR**: Pausa/reanuda la ejecución
   - ⏹️ **DETENER**: Finaliza la simulación

3. **Visualización:**
   - **Pestaña Procesos**: Tabla y gráfico de barras del estado de procesos
   - **Pestaña Memoria**: Visualización de frames ocupados/libres
   - **Pestaña Archivos**: Log de accesos al sistema de archivos

## 📊 Métricas Disponibles

| Métrica | Descripción |
|---------|-------------|
| Tiempo Promedio de Espera | Tiempo que los procesos esperan en cola |
| Tiempo Promedio de Retorno | Tiempo total desde llegada hasta finalización |
| Uso de Memoria | Porcentaje de frames ocupados |
| Page Faults | Fallos de página registrados |
| Page Hits | Accesos exitosos a páginas en memoria |
| Conflictos de Archivos | Intentos de acceso concurrente bloqueados |

## 🏗️ Arquitectura

```
┌─────────────────────────────────────┐
│     Capa de Presentación (GUI)      │
│         CustomTkinter/Tkinter       │
├─────────────────────────────────────┤
│       Capa de Controladores         │
│   Scheduler │ Memory │ FileSystem   │
├─────────────────────────────────────┤
│      Capa de Modelos de Datos       │
│    Process │ PageFrame │ Estados    │
├─────────────────────────────────────┤
│    Capa de Simulación (Threading)   │
│        Ejecución Concurrente        │
└─────────────────────────────────────┘
```

## 📁 Estructura del Proyecto

```
os-simulator/
├── main.py              # Código principal del simulador
├── README.md            # Documentación
└── docs/
    └── InformeTecnico.pdf   # Informe técnico detallado
    └── InformeDePruebas.pdf   # Informe de pruebas detallado
    └── ManuealDeUsuario.pdf   # Manual de usuario detallado
```

## 🔧 Dependencias

```txt
customtkinter>=5.0.0
```

## 👥 Autores

- **Andryw Yesid Barrera Camargo**
- **Henry Leonardo Rodriguez Paez**

## 🎓 Información Académica

- **Universidad:** Universidad Pedagógica y Tecnológica de Colombia (UPTC)
- **Facultad:** Ingeniería
- **Programa:** Ingeniería de Sistemas y Computación
- **Asignatura:** Sistemas Operativos
- **Período:** 2025-2
- **Sede:** Sogamoso, Boyacá

## 📚 Referencias

- Silberschatz, A., Galvin, P. B., & Gagne, G. (2018). *Operating System Concepts* (10th ed.). Wiley.
- Tanenbaum, A. S., & Bos, H. (2014). *Modern Operating Systems* (4th ed.). Pearson.
- [Python Threading Documentation](https://docs.python.org/3/library/threading.html)
- [CustomTkinter Documentation](https://customtkinter.tomschimansky.com/)

## 📄 Licencia

Este proyecto es de uso académico y educativo.

---

<p align="center">
  <i>Desarrollado como proyecto final de Sistemas Operativos - UPTC 2025-2</i>
</p>
