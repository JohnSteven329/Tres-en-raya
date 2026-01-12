# 🎮 Tres en Raya PRO (Tkinter)

Juego de **Tres en Raya** desarrollado en **Python + Tkinter**, con mejoras “PRO” como **CPU con dificultad**, **pista**, **deshacer**, **marcador persistente**, **soporte de teclado** y tableros **3x3 / 4x4 / 5x5**.

---

## ✨ Características

- ✅ **Modos de juego**
  - **Vs CPU** (Normal / Difícil)
  - **2 Jugadores** (local)
- ✅ **Tableros**: `3x3`, `4x4`, `5x5`  
  - En 4x4 se gana con **4 en raya**, en 5x5 con **5 en raya**.
- ✅ **Configuración desde menú**
  - Elegir **símbolo (X / O)** (en Vs CPU)
  - Elegir **quién inicia** (Humano/CPU o X/O en 2P)
  - Elegir **dificultad** (Normal / Difícil)
- ✅ **IA**
  - **Normal**: prioriza ganar > bloquear > centro > esquinas > aleatorio
  - **Difícil**:
    - En **3x3**: **Minimax + poda alpha-beta** (muy fuerte)
    - En **4x4/5x5**: usa **heurística** (minimax ahí es muy costoso)
- ✅ **Pista**: recomienda la mejor jugada del momento
- ✅ **Deshacer (Undo)**
  - En **2P**: deshace **1** jugada
  - En **Vs CPU**: deshace **2** jugadas (la tuya + la del CPU)
- ✅ **Marcador persistente**: guarda victorias/empates en un `.json`
- ✅ **Mejoras visuales**
  - Resalta la **línea ganadora**
  - Efecto **hover** y “flash” al colocar ficha
- ✅ **Teclado**
  - Flechas para moverte por el tablero
  - `Enter` o `Espacio` para jugar

---

## 🧰 Requisitos

- **Python 3.9+** recomendado
- **Tkinter** (normalmente ya viene con Python en Windows)

### Linux (Ubuntu/Debian)
Si no te abre la ventana, instala Tkinter así:

```bash
sudo apt update
sudo apt install python3-tk
