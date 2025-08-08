
import tkinter as tk
from tkinter import messagebox
import random

class TresEnRaya:
    def __init__(self, ventana, simbolo_jugador, vs_cpu=False, dificultad_cpu='Fácil', volver_menu=None):
        self.ventana = ventana
        self.ventana.title('Tres en Raya')
        self.simbolo_jugador = simbolo_jugador
        self.jugador_actual = 'X'
        self.tablero = [['' for _ in range(3)] for _ in range(3)]
        self.botones = [[None for _ in range(3)] for _ in range(3)]
        self.vs_cpu = vs_cpu
        self.dificultad_cpu = dificultad_cpu
        self.volver_menu = volver_menu
        self.frame_centro = tk.Frame(self.ventana)
        self.frame_centro.place(relx=0.5, rely=0.5, anchor='center')
        self.crear_tablero()
        # Si el jugador elige O y juega contra la CPU, la CPU (X) debe iniciar
        if self.vs_cpu and self.simbolo_jugador == 'O' and self.jugador_actual == 'X':
            self.ventana.after(400, self.jugada_cpu)

    def crear_tablero(self):
        for i in range(3):
            for j in range(3):
                btn = tk.Button(self.frame_centro, text='', font=('Arial', 32), width=5, height=2,
                                command=lambda fila=i, col=j: self.al_clic(fila, col))
                btn.grid(row=i, column=j, padx=2, pady=2)
                self.botones[i][j] = btn

    def al_clic(self, fila, col):
        if self.botones[fila][col]['text'] == '' and not self.hay_ganador():
            self.jugar(fila, col)
            if self.vs_cpu and self.jugador_actual != self.simbolo_jugador and not self.hay_ganador() and not self.tablero_lleno():
                self.ventana.after(400, self.jugada_cpu)

    def jugar(self, fila, col):
        self.botones[fila][col]['text'] = self.jugador_actual
        self.botones[fila][col]['fg'] = 'blue' if self.jugador_actual == 'X' else 'red'
        self.tablero[fila][col] = self.jugador_actual
        if self.hay_ganador():
            messagebox.showinfo('Fin del juego', f'¡{self.jugador_actual} gana!')
            self.volver_al_menu()
        elif self.tablero_lleno():
            messagebox.showinfo('Fin del juego', '¡Empate!')
            self.volver_al_menu()
        else:
            self.jugador_actual = 'O' if self.jugador_actual == 'X' else 'X'

    def jugada_cpu(self):
        if self.dificultad_cpu == 'Fácil':
            self.cpu_facil()
        elif self.dificultad_cpu == 'Normal':
            self.cpu_normal()
        else:
            self.cpu_dificil()

    def cpu_facil(self):
        vacias = [(i, j) for i in range(3) for j in range(3) if self.tablero[i][j] == '']
        if vacias:
            i, j = random.choice(vacias)
            self.jugar(i, j)

    def cpu_normal(self):
        for i in range(3):
            for j in range(3):
                if self.tablero[i][j] == '':
                    self.tablero[i][j] = self.jugador_actual
                    if self.hay_ganador():
                        self.jugar(i, j)
                        return
                    self.tablero[i][j] = ''
        rival = 'O' if self.jugador_actual == 'X' else 'X'
        for i in range(3):
            for j in range(3):
                if self.tablero[i][j] == '':
                    self.tablero[i][j] = rival
                    if self.hay_ganador():
                        self.tablero[i][j] = self.jugador_actual
                        self.jugar(i, j)
                        return
                    self.tablero[i][j] = ''
        self.cpu_facil()

    def cpu_dificil(self):
        mejor_puntaje = -float('inf')
        mejor_mov = None
        for i in range(3):
            for j in range(3):
                if self.tablero[i][j] == '':
                    self.tablero[i][j] = self.jugador_actual
                    puntaje = self.minimax(0, False)
                    self.tablero[i][j] = ''
                    if puntaje > mejor_puntaje:
                        mejor_puntaje = puntaje
                        mejor_mov = (i, j)
        if mejor_mov:
            self.jugar(*mejor_mov)

    def minimax(self, profundidad, maximizando):
        if self.hay_ganador():
            return 1 if not maximizando else -1
        if self.tablero_lleno():
            return 0
        jugador = self.jugador_actual if maximizando else ('O' if self.jugador_actual == 'X' else 'X')
        if maximizando:
            mejor = -float('inf')
            for i in range(3):
                for j in range(3):
                    if self.tablero[i][j] == '':
                        self.tablero[i][j] = jugador
                        puntaje = self.minimax(profundidad+1, False)
                        self.tablero[i][j] = ''
                        mejor = max(mejor, puntaje)
            return mejor
        else:
            mejor = float('inf')
            for i in range(3):
                for j in range(3):
                    if self.tablero[i][j] == '':
                        self.tablero[i][j] = jugador
                        puntaje = self.minimax(profundidad+1, True)
                        self.tablero[i][j] = ''
                        mejor = min(mejor, puntaje)
            return mejor

    def hay_ganador(self):
        t = self.tablero
        lineas = (
            [t[0][0], t[0][1], t[0][2]],
            [t[1][0], t[1][1], t[1][2]],
            [t[2][0], t[2][1], t[2][2]],
            [t[0][0], t[1][0], t[2][0]],
            [t[0][1], t[1][1], t[2][1]],
            [t[0][2], t[1][2], t[2][2]],
            [t[0][0], t[1][1], t[2][2]],
            [t[0][2], t[1][1], t[2][0]],
        )
        return [self.jugador_actual]*3 in lineas

    def tablero_lleno(self):
        return all(self.tablero[i][j] != '' for i in range(3) for j in range(3))

    def volver_al_menu(self):
        self.ventana.destroy()
        if self.volver_menu:
            self.volver_menu()
def menu_principal():
    ventana = tk.Tk()
    ventana.title('Tres en Raya - Menú Principal')
    ventana.geometry('400x400')
    label = tk.Label(ventana, text='Elige el modo de juego:', font=('Arial', 18))
    label.pack(pady=20)

    def elegir_dificultad():
        for widget in ventana.winfo_children():
            widget.destroy()
        label2 = tk.Label(ventana, text='Elige la dificultad de la CPU:', font=('Arial', 18))
        label2.pack(pady=20)
        for dif in ['Fácil', 'Normal', 'Difícil']:
            btn = tk.Button(ventana, text=dif, font=('Arial', 16), width=15, command=lambda d=dif: elegir_simbolo(True, d))
            btn.pack(pady=10)
        btn_back = tk.Button(ventana, text='← Volver', font=('Arial', 14), width=10, command=mostrar_menu_principal)
        btn_back.pack(pady=10)

    def elegir_simbolo(vs_cpu, dificultad_cpu='Fácil'):
        for widget in ventana.winfo_children():
            widget.destroy()
        label2 = tk.Label(ventana, text='Elige tu símbolo:', font=('Arial', 18))
        label2.pack(pady=20)
        def iniciar_juego(simbolo):
            for widget in ventana.winfo_children():
                widget.destroy()
            ventana.state('zoomed')
            TresEnRaya(ventana, simbolo, vs_cpu=vs_cpu, dificultad_cpu=dificultad_cpu, volver_menu=menu_principal)
        btn_x = tk.Button(ventana, text='Jugar como X', font=('Arial', 16), width=15, command=lambda: iniciar_juego('X'), fg='blue')
        btn_x.pack(pady=10)
        btn_o = tk.Button(ventana, text='Jugar como O', font=('Arial', 16), width=15, command=lambda: iniciar_juego('O'), fg='red')
        btn_o.pack(pady=10)
        btn_back = tk.Button(ventana, text='← Volver', font=('Arial', 14), width=10, command=mostrar_menu_principal)
        btn_back.pack(pady=10)

    def dos_jugadores():
        for widget in ventana.winfo_children():
            widget.destroy()
        ventana.state('zoomed')
        TresEnRaya(ventana, 'X', vs_cpu=False, volver_menu=menu_principal)

    def mostrar_menu_principal():
        for widget in ventana.winfo_children():
            widget.destroy()
        label = tk.Label(ventana, text='Elige el modo de juego:', font=('Arial', 18))
        label.pack(pady=20)
        btn_cpu = tk.Button(ventana, text='Jugar contra CPU', font=('Arial', 16), width=20, command=elegir_dificultad)
        btn_cpu.pack(pady=15)
        btn_2p = tk.Button(ventana, text='Jugar de 2 jugadores', font=('Arial', 16), width=20, command=dos_jugadores)
        btn_2p.pack(pady=15)
        btn_salir = tk.Button(ventana, text='Salir', font=('Arial', 14), width=10, command=ventana.destroy, fg='red')
        btn_salir.pack(pady=10)

    mostrar_menu_principal()
    ventana.mainloop()

if __name__ == '__main__':
    menu_principal()
