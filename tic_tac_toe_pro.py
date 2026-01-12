from __future__ import annotations

import argparse
import json
import random
import sys

try:
    import tkinter as tk
    from tkinter import messagebox
    TK_AVAILABLE = True
except ModuleNotFoundError:
    tk = None
    messagebox = None
    TK_AVAILABLE = False

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

Pos = Tuple[int, int]

class Mode(str, Enum):
    CPU = "CPU"
    TWO_PLAYERS = "2P"

class Difficulty(str, Enum):
    NORMAL = "Normal"
    HARD = "Difícil"

class Symbol(str, Enum):
    X = "X"
    O = "O"

SCORE_FILE = Path(__file__).with_name("tic_tac_toe_scores.json")

@dataclass
class GameLogic:
    size: int = 3
    win_len: int = 3
    board: List[List[str]] = field(default_factory=list)
    history: List[Tuple[int, int, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.board = [["" for _ in range(self.size)] for _ in range(self.size)]
        self.history = []

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.size and 0 <= c < self.size

    def available_moves(self) -> List[Pos]:
        return [(r, c) for r in range(self.size) for c in range(self.size) if self.board[r][c] == ""]

    def make_move(self, r: int, c: int, sym: str) -> bool:
        if not self.in_bounds(r, c) or self.board[r][c] != "":
            return False
        self.board[r][c] = sym
        self.history.append((r, c, sym))
        return True

    def undo(self, steps: int = 1) -> List[Tuple[int, int, str]]:
        undone: List[Tuple[int, int, str]] = []
        for _ in range(steps):
            if not self.history:
                break
            r, c, sym = self.history.pop()
            self.board[r][c] = ""
            undone.append((r, c, sym))
        return undone

    def get_winner(self) -> Tuple[Optional[str], Optional[List[Pos]]]:
        """
        Devuelve (símbolo_ganador, línea_ganadora) o (None, None).
        Funciona para NxN y K en raya (win_len).
        """
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        n = self.size
        k = self.win_len

        for r in range(n):
            for c in range(n):
                sym = self.board[r][c]
                if sym == "":
                    continue
                for dr, dc in directions:
                    line = [(r, c)]
                    rr, cc = r, c
                    for _ in range(k - 1):
                        rr += dr
                        cc += dc
                        if not self.in_bounds(rr, cc) or self.board[rr][cc] != sym:
                            break
                        line.append((rr, cc))
                    if len(line) == k:
                        return sym, line
        return None, None

    def is_draw(self) -> bool:
        winner, _ = self.get_winner()
        return winner is None and all(self.board[r][c] != "" for r in range(self.size) for c in range(self.size))

def _try_winning_move(logic: GameLogic, sym: str) -> Optional[Pos]:
    for r, c in logic.available_moves():
        logic.board[r][c] = sym
        winner, _ = logic.get_winner()
        logic.board[r][c] = ""
        if winner == sym:
            return (r, c)
    return None

def cpu_normal_move(logic: GameLogic, cpu_sym: str, opp_sym: str) -> Optional[Pos]:
    moves = logic.available_moves()
    if not moves:
        return None

    win = _try_winning_move(logic, cpu_sym)
    if win:
        return win

    block = _try_winning_move(logic, opp_sym)
    if block:
        return block

    centers: List[Pos] = []
    mid = logic.size // 2
    if logic.size % 2 == 1:
        centers = [(mid, mid)]
    else:
        centers = [(mid - 1, mid - 1), (mid - 1, mid), (mid, mid - 1), (mid, mid)]
    centers = [p for p in centers if logic.board[p[0]][p[1]] == ""]
    if centers:
        return random.choice(centers)

    corners = [(0, 0), (0, logic.size - 1), (logic.size - 1, 0), (logic.size - 1, logic.size - 1)]
    corners = [p for p in corners if logic.board[p[0]][p[1]] == ""]
    if corners:
        return random.choice(corners)

    return random.choice(moves)

def minimax_best_move_3x3(board: List[List[str]], cpu_sym: str, human_sym: str) -> Optional[Pos]:

    def available() -> List[Pos]:
        return [(r, c) for r in range(3) for c in range(3) if board[r][c] == ""]

    def get_winner() -> Optional[str]:
        lines = [
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            [(0, 0), (1, 1), (2, 2)],
            [(0, 2), (1, 1), (2, 0)],
        ]
        for sym in (Symbol.X.value, Symbol.O.value):
            for line in lines:
                if all(board[r][c] == sym for r, c in line):
                    return sym
        return None

    def is_draw() -> bool:
        return get_winner() is None and all(board[r][c] != "" for r in range(3) for c in range(3))

    def minimax(depth: int, player: str, alpha: int, beta: int) -> int:
        winner = get_winner()
        if winner == cpu_sym:
            return 10 - depth
        if winner == human_sym:
            return -10 + depth
        if is_draw():
            return 0

        moves = available()
        if player == cpu_sym:
            best = -10**9
            for r, c in moves:
                board[r][c] = cpu_sym
                score = minimax(depth + 1, human_sym, alpha, beta)
                board[r][c] = ""
                best = max(best, score)
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
            return best
        else:
            best = 10**9
            for r, c in moves:
                board[r][c] = human_sym
                score = minimax(depth + 1, cpu_sym, alpha, beta)
                board[r][c] = ""
                best = min(best, score)
                beta = min(beta, best)
                if beta <= alpha:
                    break
            return best

    moves = available()
    if not moves:
        return None

    best_score = -10**9
    best_moves: List[Pos] = []
    for r, c in moves:
        board[r][c] = cpu_sym
        score = minimax(depth=0, player=human_sym, alpha=-10**9, beta=10**9)
        board[r][c] = ""
        if score > best_score:
            best_score = score
            best_moves = [(r, c)]
        elif score == best_score:
            best_moves.append((r, c))
    return random.choice(best_moves) if best_moves else random.choice(moves)

def heuristic_move_nxn(logic: GameLogic, me: str, opp: str) -> Optional[Pos]:
    """
    Para NxN (especialmente >3), minimax es carísimo.
    Heurística simple:
      - ganar / bloquear (1 jugada)
      - luego escoger movimiento con mayor puntuación por “construir” líneas
    """
    moves = logic.available_moves()
    if not moves:
        return None

    win = _try_winning_move(logic, me)
    if win:
        return win
    block = _try_winning_move(logic, opp)
    if block:
        return block

    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    def score_move(r: int, c: int, sym: str) -> int:

        total = 0
        for dr, dc in directions:
            count = 1
            open_ends = 0

            rr, cc = r + dr, c + dc
            while logic.in_bounds(rr, cc) and logic.board[rr][cc] == sym:
                count += 1
                rr, cc = rr + dr, cc + dc
            if logic.in_bounds(rr, cc) and logic.board[rr][cc] == "":
                open_ends += 1

            rr, cc = r - dr, c - dc
            while logic.in_bounds(rr, cc) and logic.board[rr][cc] == sym:
                count += 1
                rr, cc = rr - dr, cc - dc
            if logic.in_bounds(rr, cc) and logic.board[rr][cc] == "":
                open_ends += 1

            total += (count * count) * (1 + open_ends)
        return total

    best_score = -1
    best: List[Pos] = []
    for r, c in moves:

        logic.board[r][c] = me
        s = score_move(r, c, me)
        logic.board[r][c] = ""
        logic.board[r][c] = opp
        s += score_move(r, c, opp) // 2
        logic.board[r][c] = ""
        if s > best_score:
            best_score = s
            best = [(r, c)]
        elif s == best_score:
            best.append((r, c))

    if best and random.random() < 0.15:
        return cpu_normal_move(logic, me, opp)
    return random.choice(best) if best else random.choice(moves)

def _default_scores() -> Dict[str, Dict[str, int]]:
    return {
        "CPU": {"human": 0, "cpu": 0, "draw": 0},
        "2P": {"X": 0, "O": 0, "draw": 0},
    }

def load_scores() -> Dict[str, Dict[str, int]]:
    try:
        if SCORE_FILE.exists():
            data = json.loads(SCORE_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):

                for k in _default_scores().keys():
                    data.setdefault(k, _default_scores()[k])
                return data
    except Exception:
        pass
    return _default_scores()

def save_scores(scores: Dict[str, Dict[str, int]]) -> None:
    try:
        SCORE_FILE.write_text(json.dumps(scores, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:

        pass

if TK_AVAILABLE:

    class App(tk.Tk):
        def __init__(self) -> None:
            super().__init__()
            self.title("Tres en Raya — Mejorado")
            self.minsize(520, 560)

            self._scores = load_scores()

            self.container = tk.Frame(self)
            self.container.pack(fill="both", expand=True)

            self.menu = MenuFrame(self.container, on_start=self.start_game)
            self.menu.pack(fill="both", expand=True)

            self.game: Optional[GameFrame] = None

        def start_game(
            self,
            mode: Mode,
            human_symbol: Symbol,
            difficulty: Difficulty,
            starter: str,
            size: int,
        ) -> None:
            if self.game is not None:
                self.game.destroy()
                self.game = None

            self.menu.pack_forget()
            self.game = GameFrame(
                self.container,
                mode=mode,
                human_symbol=human_symbol.value,
                difficulty=difficulty,
                starter=starter,
                size=size,
                scores=self._scores,
                on_scores_change=self._on_scores_change,
                on_menu=self.back_to_menu,
            )
            self.game.pack(fill="both", expand=True)
            self.game.focus_set()

        def back_to_menu(self) -> None:
            if self.game is not None:
                self.game.destroy()
                self.game = None
            self.menu.pack(fill="both", expand=True)

        def _on_scores_change(self, scores: Dict[str, Dict[str, int]]) -> None:
            self._scores = scores
            save_scores(scores)

    class MenuFrame(tk.Frame):
        def __init__(self, master: tk.Widget, on_start) -> None:
            super().__init__(master)
            self.on_start = on_start

            tk.Label(self, text="Tres en Raya", font=("Arial", 28, "bold")).pack(pady=18)
            tk.Label(self, text="Versión mejorada (CPU, marcador, pista, deshacer, teclado)", font=("Arial", 11)).pack()

            self.mode_var = tk.StringVar(value=Mode.CPU.value)
            self.sym_var = tk.StringVar(value=Symbol.X.value)
            self.diff_var = tk.StringVar(value=Difficulty.NORMAL.value)
            self.start_var = tk.StringVar(value="Humano")
            self.size_var = tk.IntVar(value=3)

            box = tk.Frame(self)
            box.pack(pady=18)

            tk.Label(box, text="Modo:", font=("Arial", 13)).grid(row=0, column=0, sticky="e", padx=10, pady=8)
            tk.Radiobutton(box, text="Vs CPU", variable=self.mode_var, value=Mode.CPU.value, command=self._refresh).grid(
                row=0, column=1, sticky="w"
            )
            tk.Radiobutton(box, text="2 Jugadores", variable=self.mode_var, value=Mode.TWO_PLAYERS.value, command=self._refresh).grid(
                row=0, column=2, sticky="w"
            )

            self.sym_row = 1
            tk.Label(box, text="Tu símbolo:", font=("Arial", 13)).grid(row=self.sym_row, column=0, sticky="e", padx=10, pady=8)
            self.rb_x = tk.Radiobutton(box, text="X", variable=self.sym_var, value=Symbol.X.value)
            self.rb_o = tk.Radiobutton(box, text="O", variable=self.sym_var, value=Symbol.O.value)
            self.rb_x.grid(row=self.sym_row, column=1, sticky="w")
            self.rb_o.grid(row=self.sym_row, column=2, sticky="w")

            self.diff_row = 2
            tk.Label(box, text="Dificultad:", font=("Arial", 13)).grid(row=self.diff_row, column=0, sticky="e", padx=10, pady=8)
            self.diff_menu = tk.OptionMenu(box, self.diff_var, Difficulty.NORMAL.value, Difficulty.HARD.value)
            self.diff_menu.config(width=10)
            self.diff_menu.grid(row=self.diff_row, column=1, sticky="w", columnspan=2)

            self.start_row = 3
            self.start_label = tk.Label(box, text="Inicia:", font=("Arial", 13))
            self.start_label.grid(row=self.start_row, column=0, sticky="e", padx=10, pady=8)
            self.start_menu = tk.OptionMenu(box, self.start_var, "Humano", "CPU")
            self.start_menu.config(width=10)
            self.start_menu.grid(row=self.start_row, column=1, sticky="w", columnspan=2)

            self.size_row = 4
            tk.Label(box, text="Tamaño:", font=("Arial", 13)).grid(row=self.size_row, column=0, sticky="e", padx=10, pady=8)
            size_box = tk.Frame(box)
            size_box.grid(row=self.size_row, column=1, sticky="w", columnspan=2)
            tk.Radiobutton(size_box, text="3x3", variable=self.size_var, value=3).pack(side="left", padx=4)
            tk.Radiobutton(size_box, text="4x4", variable=self.size_var, value=4).pack(side="left", padx=4)
            tk.Radiobutton(size_box, text="5x5", variable=self.size_var, value=5).pack(side="left", padx=4)

            self.note = tk.Label(self, text="", font=("Arial", 10), fg="#444")
            self.note.pack(pady=6)

            tk.Button(self, text="Jugar", font=("Arial", 14, "bold"), width=12, command=self._start).pack(pady=16)
            tk.Button(self, text="Salir", font=("Arial", 12), width=12, command=self.master.winfo_toplevel().destroy).pack(pady=6)

            self._refresh()

        def _refresh(self) -> None:
            mode = self.mode_var.get()
            if mode == Mode.TWO_PLAYERS.value:
                self.rb_x.config(state="disabled")
                self.rb_o.config(state="disabled")
                self.diff_menu.config(state="disabled")

                menu = self.start_menu["menu"]
                menu.delete(0, "end")
                for item in ("X", "O"):
                    menu.add_command(label=item, command=lambda v=item: self.start_var.set(v))
                if self.start_var.get() not in ("X", "O"):
                    self.start_var.set("X")
                self.note.config(text="Tip: Flechas + Enter para jugar con teclado. 'Deshacer' revierte 1 jugada.")
            else:
                self.rb_x.config(state="normal")
                self.rb_o.config(state="normal")
                self.diff_menu.config(state="normal")

                menu = self.start_menu["menu"]
                menu.delete(0, "end")
                for item in ("Humano", "CPU"):
                    menu.add_command(label=item, command=lambda v=item: self.start_var.set(v))
                if self.start_var.get() not in ("Humano", "CPU"):
                    self.start_var.set("Humano")

                size = self.size_var.get()
                if size != 3 and self.diff_var.get() == Difficulty.HARD.value:
                    self.note.config(text="Nota: En 4x4/5x5 la CPU Difícil usa heurística (minimax solo 3x3).")
                else:
                    self.note.config(text="Consejo: 'Pista' te recomienda la mejor jugada del momento.")

        def _start(self) -> None:
            mode = Mode(self.mode_var.get())
            human_symbol = Symbol(self.sym_var.get())
            difficulty = Difficulty(self.diff_var.get())
            starter = self.start_var.get()
            size = int(self.size_var.get())
            self.on_start(mode, human_symbol, difficulty, starter, size)

    class GameFrame(tk.Frame):
        def __init__(
            self,
            master: tk.Widget,
            mode: Mode,
            human_symbol: str,
            difficulty: Difficulty,
            starter: str,
            size: int,
            scores: Dict[str, Dict[str, int]],
            on_scores_change,
            on_menu,
        ) -> None:
            super().__init__(master)
            self.on_menu = on_menu
            self.on_scores_change = on_scores_change

            self.mode = mode
            self.difficulty = difficulty
            self.human_symbol = human_symbol
            self.cpu_symbol = "O" if human_symbol == "X" else "X"
            self.size = size
            self.win_len = size if size > 3 else 3

            self.logic = GameLogic(size=self.size, win_len=self.win_len)

            self.game_over = False
            self.current = "X"
            self._scores = scores

            self.buttons: List[List[tk.Button]] = []
            self._default_bg = self.cget("bg")
            self._hover_bg = "#f0f6ff"
            self._select_border = 3
            self._selected: Pos = (0, 0)
            self._hint_pos: Optional[Pos] = None

            top = tk.Frame(self)
            top.pack(fill="x", padx=10, pady=10)

            self.status = tk.Label(top, text="", font=("Arial", 13))
            self.status.pack(side="left")

            self.score_label = tk.Label(top, text="", font=("Arial", 11), fg="#444")
            self.score_label.pack(side="left", padx=12)

            tk.Button(top, text="Pista", font=("Arial", 11), command=self.show_hint).pack(side="right", padx=6)
            tk.Button(top, text="Deshacer", font=("Arial", 11), command=self.undo_move).pack(side="right", padx=6)
            tk.Button(top, text="Reiniciar", font=("Arial", 11), command=self.reset).pack(side="right", padx=6)
            tk.Button(top, text="Menú", font=("Arial", 11), command=self.back_to_menu).pack(side="right", padx=6)

            self.board_frame = tk.Frame(self)
            self.board_frame.pack(padx=10, pady=10, expand=True)

            self._build_board()

            self.bind_all("<Left>", self._on_key)
            self.bind_all("<Right>", self._on_key)
            self.bind_all("<Up>", self._on_key)
            self.bind_all("<Down>", self._on_key)
            self.bind_all("<Return>", self._on_key)
            self.bind_all("<space>", self._on_key)

            if self.mode == Mode.TWO_PLAYERS:
                self.current = starter if starter in ("X", "O") else "X"
            else:

                self.current = "X"
                if starter == "CPU":

                    if self.cpu_symbol == "X":
                        self.after(250, self.cpu_move)
                    else:

                        self.human_symbol, self.cpu_symbol = self.cpu_symbol, self.human_symbol
                        self.after(250, self.cpu_move)

            self._update_status()
            self._update_score_label()
            self._ensure_selection_on_empty()

        def _build_board(self) -> None:
            for w in self.board_frame.winfo_children():
                w.destroy()
            self.buttons = [[None for _ in range(self.size)] for _ in range(self.size)]

            for r in range(self.size):
                self.board_frame.grid_rowconfigure(r, weight=1)
                for c in range(self.size):
                    self.board_frame.grid_columnconfigure(c, weight=1)
                    btn = tk.Button(
                        self.board_frame,
                        text="",
                        font=("Arial", 26 if self.size == 3 else 20, "bold"),
                        width=3,
                        height=1,
                        command=lambda rr=r, cc=c: self.play(rr, cc),
                    )
                    btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
                    btn.bind("<Enter>", lambda e, rr=r, cc=c: self._on_hover(rr, cc, enter=True))
                    btn.bind("<Leave>", lambda e, rr=r, cc=c: self._on_hover(rr, cc, enter=False))
                    self.buttons[r][c] = btn

            self._redraw_board()

        def _redraw_board(self) -> None:
            for r in range(self.size):
                for c in range(self.size):
                    sym = self.logic.board[r][c]
                    btn = self.buttons[r][c]
                    btn.config(
                        text=sym,
                        state="normal" if (sym == "" and not self.game_over) else "disabled",
                        bg=self._default_bg,
                        fg="black" if sym != "" else "black",
                        relief="raised",
                        bd=2,
                        highlightthickness=0,
                    )
            self._apply_selection_style()

        def _flash_cell(self, r: int, c: int, color: str = "#d7f5d7") -> None:
            btn = self.buttons[r][c]
            old = btn.cget("bg")
            btn.config(bg=color)
            self.after(140, lambda: btn.config(bg=old))

        def _on_hover(self, r: int, c: int, enter: bool) -> None:
            if self.game_over:
                return
            if self.logic.board[r][c] != "":
                return
            btn = self.buttons[r][c]

            if (r, c) == self._selected:
                return
            btn.config(bg=self._hover_bg if enter else self._default_bg)

        def _apply_selection_style(self) -> None:

            for r in range(self.size):
                for c in range(self.size):
                    btn = self.buttons[r][c]
                    if (r, c) == self._selected and not self.game_over:
                        btn.config(relief="solid", bd=self._select_border)
                    else:
                        btn.config(relief="raised", bd=2)

        def _ensure_selection_on_empty(self) -> None:
            if self.logic.board[self._selected[0]][self._selected[1]] == "":
                self._apply_selection_style()
                return

            for r, c in self.logic.available_moves():
                self._selected = (r, c)
                break
            self._apply_selection_style()

        def _on_key(self, event) -> None:
            if not self.winfo_ismapped():
                return
            key = event.keysym.lower()
            if key in ("return", "space"):
                r, c = self._selected
                self.play(r, c)
                return
            if self.game_over:
                return

            r, c = self._selected
            if key == "left":
                c = (c - 1) % self.size
            elif key == "right":
                c = (c + 1) % self.size
            elif key == "up":
                r = (r - 1) % self.size
            elif key == "down":
                r = (r + 1) % self.size
            self._selected = (r, c)
            self._apply_selection_style()

        def back_to_menu(self) -> None:
            if messagebox.askyesno("Volver al menú", "¿Seguro que deseas volver al menú?"):

                self.unbind_all("<Left>")
                self.unbind_all("<Right>")
                self.unbind_all("<Up>")
                self.unbind_all("<Down>")
                self.unbind_all("<Return>")
                self.unbind_all("<space>")
                self.on_menu()

        def reset(self) -> None:
            if not messagebox.askyesno("Reiniciar", "¿Reiniciar la partida actual?"):
                return
            self.logic.reset()
            self.game_over = False
            self._hint_pos = None

            self.current = "X"
            self._redraw_board()
            self._update_status()
            self._ensure_selection_on_empty()

            if self.mode == Mode.CPU and self.cpu_symbol == "X" and self._starter_is_cpu():
                self.after(250, self.cpu_move)

        def _starter_is_cpu(self) -> bool:

            return len(self.logic.history) == 0

        def undo_move(self) -> None:
            if not self.logic.history:
                return

            if self.mode == Mode.TWO_PLAYERS:
                undone = self.logic.undo(1)
            else:

                undone = self.logic.undo(2 if len(self.logic.history) >= 2 else 1)

            if not undone:
                return

            self.game_over = False
            self._hint_pos = None

            if self.mode == Mode.TWO_PLAYERS:
                self.current = undone[0][2]
            else:

                self.current = "X" if (len(self.logic.history) % 2 == 0) else "O"

                self.current = self._next_symbol_by_count()

            self._redraw_board()
            self._update_status()
            self._ensure_selection_on_empty()

        def _next_symbol_by_count(self) -> str:
            x = sum(1 for r in range(self.size) for c in range(self.size) if self.logic.board[r][c] == "X")
            o = sum(1 for r in range(self.size) for c in range(self.size) if self.logic.board[r][c] == "O")
            return "X" if x == o else "O"

        def play(self, r: int, c: int) -> None:
            if self.game_over:
                return
            if self.logic.board[r][c] != "":
                return

            if self.mode == Mode.CPU and self.current != self.human_symbol:
                return

            if not self.logic.make_move(r, c, self.current):
                return

            self._hint_pos = None
            self._flash_cell(r, c)
            self._redraw_board()
            self._ensure_selection_on_empty()

            if self._end_if_needed():
                return

            self.current = "O" if self.current == "X" else "X"
            self._update_status()

            if self.mode == Mode.CPU:
                self.after(260, self.cpu_move)

        def _end_if_needed(self) -> bool:
            winner, line = self.logic.get_winner()
            if winner:
                self.game_over = True
                self._highlight_winner_line(line or [])
                self._update_score(winner)
                self._update_status(final=True, winner=winner)
                messagebox.showinfo("Fin del juego", f"¡Ganó {winner}!")
                return True

            if self.logic.is_draw():
                self.game_over = True
                self._update_score("draw")
                self._update_status(final=True, winner=None)
                messagebox.showinfo("Fin del juego", "¡Empate!")
                return True

            return False

        def cpu_move(self) -> None:
            if self.game_over or self.mode != Mode.CPU:
                return
            if self.current != self.cpu_symbol:
                return

            move = None
            if self.difficulty == Difficulty.NORMAL:
                move = cpu_normal_move(self.logic, self.cpu_symbol, self.human_symbol)
            else:
                if self.size == 3 and self.win_len == 3:

                    move = minimax_best_move_3x3(self.logic.board, self.cpu_symbol, self.human_symbol)
                else:
                    move = heuristic_move_nxn(self.logic, self.cpu_symbol, self.human_symbol)

            if move is None:
                return
            r, c = move
            self.logic.make_move(r, c, self.cpu_symbol)
            self._flash_cell(r, c, color="#ffe8cc")
            self._redraw_board()
            self._ensure_selection_on_empty()

            if self._end_if_needed():
                return

            self.current = self.human_symbol
            self._update_status()

        def show_hint(self) -> None:
            if self.game_over:
                return

            if self.mode == Mode.CPU and self.current != self.human_symbol:
                return

            pos = self._compute_hint()
            if not pos:
                return

            self._hint_pos = pos
            r, c = pos
            btn = self.buttons[r][c]
            old = btn.cget("bg")
            btn.config(bg="#fff3b0")
            self.after(450, lambda: (btn.config(bg=old), self._hint_clear_if_same(pos)))

        def _hint_clear_if_same(self, pos: Pos) -> None:
            if self._hint_pos == pos:
                self._hint_pos = None

        def _compute_hint(self) -> Optional[Pos]:
            moves = self.logic.available_moves()
            if not moves:
                return None

            win = _try_winning_move(self.logic, self.current)
            if win:
                return win

            if self.size == 3 and self.win_len == 3:

                if self.current == self.cpu_symbol and self.mode == Mode.CPU:
                    return minimax_best_move_3x3(self.logic.board, self.cpu_symbol, self.human_symbol)

                other = "O" if self.current == "X" else "X"
                return minimax_best_move_3x3(self.logic.board, cpu_sym=self.current, human_sym=other)

            other = "O" if self.current == "X" else "X"
            return heuristic_move_nxn(self.logic, me=self.current, opp=other)

        def _update_score(self, winner: str) -> None:
            if self.mode == Mode.CPU:
                if winner == "draw":
                    self._scores["CPU"]["draw"] += 1
                elif winner == self.human_symbol:
                    self._scores["CPU"]["human"] += 1
                else:
                    self._scores["CPU"]["cpu"] += 1
            else:
                if winner == "draw":
                    self._scores["2P"]["draw"] += 1
                elif winner in ("X", "O"):
                    self._scores["2P"][winner] += 1

            self._update_score_label()
            self.on_scores_change(self._scores)

        def _update_score_label(self) -> None:
            if self.mode == Mode.CPU:
                s = self._scores["CPU"]
                self.score_label.config(text=f"Marcador: Tú {s['human']} | CPU {s['cpu']} | Empates {s['draw']}")
            else:
                s = self._scores["2P"]
                self.score_label.config(text=f"Marcador: X {s['X']} | O {s['O']} | Empates {s['draw']}")

        def _update_status(self, final: bool = False, winner: Optional[str] = None) -> None:
            if final:
                if winner:
                    self.status.config(text=f"Ganador: {winner}")
                else:
                    self.status.config(text="Empate")
                return

            if self.mode == Mode.TWO_PLAYERS:
                self.status.config(text=f"Turno: {self.current}")
            else:
                who = "Tú" if self.current == self.human_symbol else "CPU"
                self.status.config(text=f"Turno: {who} ({self.current})")

        def _highlight_winner_line(self, line: List[Pos]) -> None:
            for r, c in line:
                self.buttons[r][c].config(bg="#c7f9cc")

            for r in range(self.size):
                for c in range(self.size):
                    self.buttons[r][c].config(state="disabled")

        def destroy(self) -> None:

            try:
                self.unbind_all("<Left>")
                self.unbind_all("<Right>")
                self.unbind_all("<Up>")
                self.unbind_all("<Down>")
                self.unbind_all("<Return>")
                self.unbind_all("<space>")
            except Exception:
                pass
            super().destroy()

def run_tests() -> int:
    import unittest

    class TestGameLogic(unittest.TestCase):
        def test_winner_3x3_row(self):
            g = GameLogic(3, 3)
            g.make_move(0, 0, "X")
            g.make_move(0, 1, "X")
            g.make_move(0, 2, "X")
            w, line = g.get_winner()
            self.assertEqual(w, "X")
            self.assertEqual(set(line or []), {(0, 0), (0, 1), (0, 2)})

        def test_winner_3x3_diag(self):
            g = GameLogic(3, 3)
            g.make_move(0, 0, "O")
            g.make_move(1, 1, "O")
            g.make_move(2, 2, "O")
            w, _ = g.get_winner()
            self.assertEqual(w, "O")

        def test_draw_3x3(self):
            g = GameLogic(3, 3)

            seq = [
                (0, 0, "X"), (0, 1, "O"), (0, 2, "X"),
                (1, 0, "X"), (1, 1, "O"), (1, 2, "O"),
                (2, 0, "O"), (2, 1, "X"), (2, 2, "X"),
            ]
            for r, c, s in seq:
                g.make_move(r, c, s)
            self.assertTrue(g.is_draw())

        def test_winner_4x4(self):
            g = GameLogic(4, 4)
            for c in range(4):
                g.make_move(2, c, "X")
            w, _ = g.get_winner()
            self.assertEqual(w, "X")

        def test_minimax_winning_move(self):

            board = [
                ["X", "X", ""],
                ["O", "O", ""],
                ["", "", ""],
            ]
            move = minimax_best_move_3x3(board, cpu_sym="X", human_sym="O")
            self.assertEqual(move, (0, 2))

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestGameLogic)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1

def main() -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--test", action="store_true", help="Ejecuta tests de lógica y sale")
    args = parser.parse_args()

    if args.test:
        return run_tests()

    if not TK_AVAILABLE:
        print("Error: tkinter no está disponible en este entorno. Ejecuta este juego en un Python con soporte de interfaz (Tkinter).")
        return 1
    app = App()
    app.mainloop()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
