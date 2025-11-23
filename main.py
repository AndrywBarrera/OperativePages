"""
SIMULADOR DE SISTEMA OPERATIVO CON INTERFAZ GRÁFICA MODERNA
Proyecto de Sistemas Operativos 2025-2
Incluye: Planificación de procesos, Gestión de memoria, Gestión de archivos
Interfaz: CustomTkinter (GUI moderna)
"""

import time
import random
import threading
from collections import deque
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import tkinter as tk
from tkinter import ttk

try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
except ImportError:
    CTK_AVAILABLE = False
    print("CustomTkinter no está instalado. Instalalo con: pip install customtkinter")

# ==================== ESTRUCTURAS DE DATOS ====================

class ProcessState(Enum):
    NEW = "NUEVO"
    READY = "LISTO"
    RUNNING = "EJECUTANDO"
    WAITING = "ESPERANDO"
    TERMINATED = "TERMINADO"

@dataclass
class Process:
    pid: int
    priority: int
    burst_time: int
    remaining_time: int
    arrival_time: float
    start_time: Optional[float] = None
    finish_time: Optional[float] = None
    waiting_time: float = 0
    state: ProcessState = ProcessState.NEW
    pages_needed: List[int] = field(default_factory=list)
    file_access: List[str] = field(default_factory=list)
    color: str = ""
    
    def __post_init__(self):
        if not self.pages_needed:
            self.pages_needed = [random.randint(0, 19) for _ in range(random.randint(3, 8))]
        if not self.file_access:
            files = ["archivo1.txt", "archivo2.txt", "archivo3.txt"]
            self.file_access = random.sample(files, random.randint(1, 2))
        if not self.color:
            self.color = f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"

@dataclass
class PageFrame:
    page_number: Optional[int] = None
    process_id: Optional[int] = None
    last_access_time: float = 0
    load_time: float = 0

class FileSystem:
    def __init__(self):
        self.files: Dict[str, threading.Lock] = {
            "archivo1.txt": threading.Lock(),
            "archivo2.txt": threading.Lock(),
            "archivo3.txt": threading.Lock()
        }
        self.access_log: List[Dict] = []
        self.conflicts: int = 0
    
    def access_file(self, filename: str, process_id: int, mode: str = "read"):
        acquired = self.files[filename].acquire(blocking=False)
        
        if acquired:
            self.access_log.append({
                'process': process_id,
                'file': filename,
                'mode': mode,
                'status': 'SUCCESS',
                'time': time.time()
            })
            time.sleep(0.01)
            self.files[filename].release()
            return True
        else:
            self.conflicts += 1
            self.access_log.append({
                'process': process_id,
                'file': filename,
                'mode': mode,
                'status': 'CONFLICT',
                'time': time.time()
            })
            return False

# ==================== GESTIÓN DE MEMORIA ====================

class MemoryManager:
    def __init__(self, num_frames: int = 10):
        self.num_frames = num_frames
        self.frames: List[PageFrame] = [PageFrame() for _ in range(num_frames)]
        self.page_faults = 0
        self.page_hits = 0
        self.replacement_algorithm = "LRU"
    
    def access_page(self, page_number: int, process_id: int) -> bool:
        current_time = time.time()
        
        for frame in self.frames:
            if frame.page_number == page_number and frame.process_id == process_id:
                frame.last_access_time = current_time
                self.page_hits += 1
                return False
        
        self.page_faults += 1
        self._load_page(page_number, process_id, current_time)
        return True
    
    def _load_page(self, page_number: int, process_id: int, current_time: float):
        for frame in self.frames:
            if frame.page_number is None:
                frame.page_number = page_number
                frame.process_id = process_id
                frame.last_access_time = current_time
                frame.load_time = current_time
                return
        
        if self.replacement_algorithm == "FIFO":
            victim = min(self.frames, key=lambda f: f.load_time)
        else:
            victim = min(self.frames, key=lambda f: f.last_access_time)
        
        victim.page_number = page_number
        victim.process_id = process_id
        victim.last_access_time = current_time
        victim.load_time = current_time
    
    def get_memory_usage(self) -> float:
        occupied = sum(1 for f in self.frames if f.page_number is not None)
        return (occupied / self.num_frames) * 100

# ==================== PLANIFICACIÓN DE PROCESOS ====================

class Scheduler:
    def __init__(self, algorithm: str = "RR", quantum: int = 2):
        self.algorithm = algorithm
        self.quantum = quantum
        self.ready_queue = deque()
        self.completed_processes: List[Process] = []
        self.current_time = 0
        self.metrics = {
            'total_waiting_time': 0,
            'total_turnaround_time': 0,
            'total_processes': 0
        }
    
    def add_process(self, process: Process):
        process.state = ProcessState.READY
        process.arrival_time = self.current_time
        self.ready_queue.append(process)
        self._sort_queue()
    
    def _sort_queue(self):
        if self.algorithm == "SJF":
            self.ready_queue = deque(sorted(self.ready_queue, key=lambda p: p.remaining_time))
        elif self.algorithm == "PRIORITY":
            self.ready_queue = deque(sorted(self.ready_queue, key=lambda p: p.priority))
    
    def get_next_process(self) -> Optional[Process]:
        if not self.ready_queue:
            return None
        
        process = self.ready_queue.popleft()
        process.state = ProcessState.RUNNING
        
        if process.start_time is None:
            process.start_time = self.current_time
        
        return process
    
    def execute_process(self, process: Process, memory: MemoryManager, 
                       filesystem: FileSystem) -> bool:
        if process.remaining_time <= 0:
            return True
        
        execution_time = min(self.quantum if self.algorithm == "RR" else process.remaining_time, 
                           process.remaining_time)
        
        if process.pages_needed:
            page = random.choice(process.pages_needed)
            memory.access_page(page, process.pid)
        
        if random.random() < 0.2 and process.file_access:
            file = random.choice(process.file_access)
            filesystem.access_file(file, process.pid)
        
        process.remaining_time -= execution_time
        self.current_time += execution_time
        
        if process.remaining_time <= 0:
            process.state = ProcessState.TERMINATED
            process.finish_time = self.current_time
            process.waiting_time = process.finish_time - process.arrival_time - process.burst_time
            self.completed_processes.append(process)
            self._update_metrics(process)
            return True
        else:
            process.state = ProcessState.READY
            self.ready_queue.append(process)
            if self.algorithm != "RR":
                self._sort_queue()
            return False
    
    def _update_metrics(self, process: Process):
        self.metrics['total_processes'] += 1
        self.metrics['total_waiting_time'] += process.waiting_time
        turnaround = process.finish_time - process.arrival_time
        self.metrics['total_turnaround_time'] += turnaround
    
    def get_metrics(self) -> Dict:
        n = self.metrics['total_processes']
        if n == 0:
            return {'avg_waiting_time': 0, 'avg_turnaround_time': 0, 'total_processes': 0}
        
        return {
            'avg_waiting_time': self.metrics['total_waiting_time'] / n,
            'avg_turnaround_time': self.metrics['total_turnaround_time'] / n,
            'total_processes': n
        }

# ==================== INTERFAZ GRÁFICA MODERNA ====================

class OSSimulatorGUI:
    def __init__(self):
        if CTK_AVAILABLE:
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
            self.root = ctk.CTk()
        else:
            self.root = tk.Tk()
            self.root.configure(bg="#1a1a1a")
        
        self.root.title("Simulador de Sistema Operativo - 2025-2")
        self.root.geometry("1400x900")
        
        self.scheduler = None
        self.memory = None
        self.filesystem = None
        self.processes = []
        self.running = False
        self.paused = False
        self.simulation_thread = None
        
        self.create_widgets()
    
    def create_widgets(self):
        # Header
        if CTK_AVAILABLE:
            header = ctk.CTkFrame(self.root, height=80, corner_radius=0)
        else:
            header = tk.Frame(self.root, bg="#2b2b2b", height=80)
        header.pack(fill="x", padx=0, pady=0)
        
        if CTK_AVAILABLE:
            title = ctk.CTkLabel(header, text="🖥️ SIMULADOR DE SISTEMA OPERATIVO", 
                                font=("Arial", 24, "bold"))
        else:
            title = tk.Label(header, text="🖥️ SIMULADOR DE SISTEMA OPERATIVO",
                           font=("Arial", 24, "bold"), bg="#2b2b2b", fg="white")
        title.pack(pady=20)
        
        # Main container
        main_container = tk.Frame(self.root, bg="#1a1a1a")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel (Controles)
        if CTK_AVAILABLE:
            left_panel = ctk.CTkFrame(main_container, width=300)
        else:
            left_panel = tk.Frame(main_container, bg="#2b2b2b", width=300)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        
        self.create_control_panel(left_panel)
        
        # Right panel (Visualización)
        if CTK_AVAILABLE:
            right_panel = ctk.CTkFrame(main_container)
        else:
            right_panel = tk.Frame(main_container, bg="#2b2b2b")
        right_panel.pack(side="right", fill="both", expand=True)
        
        self.create_visualization_panel(right_panel)
    
    def create_control_panel(self, parent):
        if CTK_AVAILABLE:
            title = ctk.CTkLabel(parent, text="⚙️ CONFIGURACIÓN", 
                               font=("Arial", 16, "bold"))
        else:
            title = tk.Label(parent, text="⚙️ CONFIGURACIÓN",
                           font=("Arial", 16, "bold"), bg="#2b2b2b", fg="white")
        title.pack(pady=15)
        
        # Algoritmo
        if CTK_AVAILABLE:
            ctk.CTkLabel(parent, text="Algoritmo de Planificación:").pack(pady=5)
            self.algo_var = tk.StringVar(value="RR")
            algo_menu = ctk.CTkOptionMenu(parent, variable=self.algo_var,
                                         values=["RR", "SJF", "PRIORITY"])
        else:
            tk.Label(parent, text="Algoritmo de Planificación:", 
                    bg="#2b2b2b", fg="white").pack(pady=5)
            self.algo_var = tk.StringVar(value="RR")
            algo_menu = ttk.Combobox(parent, textvariable=self.algo_var,
                                    values=["RR", "SJF", "PRIORITY"], state="readonly")
        algo_menu.pack(pady=5, padx=20, fill="x")
        
        # Número de procesos
        if CTK_AVAILABLE:
            ctk.CTkLabel(parent, text="Número de Procesos:").pack(pady=5)
            self.num_processes_var = tk.StringVar(value="8")
            num_entry = ctk.CTkEntry(parent, textvariable=self.num_processes_var)
        else:
            tk.Label(parent, text="Número de Procesos:", 
                    bg="#2b2b2b", fg="white").pack(pady=5)
            self.num_processes_var = tk.StringVar(value="8")
            num_entry = tk.Entry(parent, textvariable=self.num_processes_var)
        num_entry.pack(pady=5, padx=20, fill="x")
        
        # Quantum
        if CTK_AVAILABLE:
            ctk.CTkLabel(parent, text="Quantum (RR):").pack(pady=5)
            self.quantum_var = tk.StringVar(value="2")
            quantum_entry = ctk.CTkEntry(parent, textvariable=self.quantum_var)
        else:
            tk.Label(parent, text="Quantum (RR):", 
                    bg="#2b2b2b", fg="white").pack(pady=5)
            self.quantum_var = tk.StringVar(value="2")
            quantum_entry = tk.Entry(parent, textvariable=self.quantum_var)
        quantum_entry.pack(pady=5, padx=20, fill="x")
        
        # Frames de memoria
        if CTK_AVAILABLE:
            ctk.CTkLabel(parent, text="Frames de Memoria:").pack(pady=5)
            self.frames_var = tk.StringVar(value="10")
            frames_entry = ctk.CTkEntry(parent, textvariable=self.frames_var)
        else:
            tk.Label(parent, text="Frames de Memoria:", 
                    bg="#2b2b2b", fg="white").pack(pady=5)
            self.frames_var = tk.StringVar(value="10")
            frames_entry = tk.Entry(parent, textvariable=self.frames_var)
        frames_entry.pack(pady=5, padx=20, fill="x")
        
        # Botones
        btn_frame = tk.Frame(parent, bg="#2b2b2b" if not CTK_AVAILABLE else None)
        btn_frame.pack(pady=20, fill="x", padx=20)
        
        if CTK_AVAILABLE:
            self.start_btn = ctk.CTkButton(btn_frame, text="▶️ INICIAR", 
                                          command=self.start_simulation,
                                          fg_color="#2ecc71", hover_color="#27ae60")
        else:
            self.start_btn = tk.Button(btn_frame, text="▶️ INICIAR",
                                      command=self.start_simulation,
                                      bg="#2ecc71", fg="white", font=("Arial", 10, "bold"))
        self.start_btn.pack(fill="x", pady=5)
        
        if CTK_AVAILABLE:
            self.pause_btn = ctk.CTkButton(btn_frame, text="⏸️ PAUSAR",
                                          command=self.pause_simulation,
                                          fg_color="#f39c12", hover_color="#e67e22")
        else:
            self.pause_btn = tk.Button(btn_frame, text="⏸️ PAUSAR",
                                      command=self.pause_simulation,
                                      bg="#f39c12", fg="white", font=("Arial", 10, "bold"))
        self.pause_btn.pack(fill="x", pady=5)
        self.pause_btn.configure(state="disabled")
        
        if CTK_AVAILABLE:
            self.stop_btn = ctk.CTkButton(btn_frame, text="⏹️ DETENER",
                                         command=self.stop_simulation,
                                         fg_color="#e74c3c", hover_color="#c0392b")
        else:
            self.stop_btn = tk.Button(btn_frame, text="⏹️ DETENER",
                                     command=self.stop_simulation,
                                     bg="#e74c3c", fg="white", font=("Arial", 10, "bold"))
        self.stop_btn.pack(fill="x", pady=5)
        self.stop_btn.configure(state="disabled")
        
        # Métricas en tiempo real
        if CTK_AVAILABLE:
            metrics_frame = ctk.CTkFrame(parent)
        else:
            metrics_frame = tk.Frame(parent, bg="#1a1a1a")
        metrics_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        if CTK_AVAILABLE:
            ctk.CTkLabel(metrics_frame, text="📊 MÉTRICAS", 
                        font=("Arial", 14, "bold")).pack(pady=10)
        else:
            tk.Label(metrics_frame, text="📊 MÉTRICAS",
                    font=("Arial", 14, "bold"), bg="#1a1a1a", fg="white").pack(pady=10)
        
        if CTK_AVAILABLE:
            self.metrics_text = ctk.CTkTextbox(metrics_frame, height=200, width=250)
        else:
            self.metrics_text = tk.Text(metrics_frame, height=12, width=30,
                                       bg="#1a1a1a", fg="white", font=("Courier", 9))
        self.metrics_text.pack(fill="both", expand=True, padx=10, pady=5)
    
    def create_visualization_panel(self, parent):
        # Notebook/Tabs
        if CTK_AVAILABLE:
            tabview = ctk.CTkTabview(parent)
            tabview.pack(fill="both", expand=True, padx=10, pady=10)
            
            tab1 = tabview.add("Procesos")
            tab2 = tabview.add("Memoria")
            tab3 = tabview.add("Archivos")
        else:
            notebook = ttk.Notebook(parent)
            notebook.pack(fill="both", expand=True, padx=10, pady=10)
            
            tab1 = tk.Frame(notebook, bg="#1a1a1a")
            tab2 = tk.Frame(notebook, bg="#1a1a1a")
            tab3 = tk.Frame(notebook, bg="#1a1a1a")
            
            notebook.add(tab1, text="Procesos")
            notebook.add(tab2, text="Memoria")
            notebook.add(tab3, text="Archivos")
        
        # Tab 1: Procesos
        self.create_process_tab(tab1)
        
        # Tab 2: Memoria
        self.create_memory_tab(tab2)
        
        # Tab 3: Archivos
        self.create_files_tab(tab3)
    
    def create_process_tab(self, parent):
        # Canvas para visualización de procesos
        canvas_frame = tk.Frame(parent, bg="#1a1a1a")
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.process_canvas = tk.Canvas(canvas_frame, bg="#2b2b2b", 
                                       highlightthickness=0, height=200)
        self.process_canvas.pack(fill="x", pady=10)
        
        # Tabla de procesos
        if CTK_AVAILABLE:
            table_frame = ctk.CTkFrame(parent)
        else:
            table_frame = tk.Frame(parent, bg="#2b2b2b")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("PID", "Estado", "Prioridad", "Burst", "Restante", "Espera")
        self.process_tree = ttk.Treeview(table_frame, columns=columns, 
                                        show="headings", height=15)
        
        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", 
                                 command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)
        
        self.process_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_memory_tab(self, parent):
        # Canvas para visualización de memoria
        self.memory_canvas = tk.Canvas(parent, bg="#2b2b2b", 
                                      highlightthickness=0)
        self.memory_canvas.pack(fill="both", expand=True, padx=20, pady=20)
    
    def create_files_tab(self, parent):
        if CTK_AVAILABLE:
            self.files_text = ctk.CTkTextbox(parent)
        else:
            self.files_text = tk.Text(parent, bg="#1a1a1a", fg="white",
                                     font=("Courier", 10))
        self.files_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def start_simulation(self):
        if self.running:
            return
        
        try:
            num_proc = int(self.num_processes_var.get())
            quantum = int(self.quantum_var.get())
            frames = int(self.frames_var.get())
        except ValueError:
            return
        
        self.running = True
        self.paused = False
        
        self.scheduler = Scheduler(algorithm=self.algo_var.get(), quantum=quantum)
        self.memory = MemoryManager(num_frames=frames)
        self.filesystem = FileSystem()
        self.processes = self._generate_processes(num_proc)
        
        for process in self.processes:
            self.scheduler.add_process(process)
        
        self.start_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal")
        self.stop_btn.configure(state="normal")
        
        self.simulation_thread = threading.Thread(target=self.run_simulation, daemon=True)
        self.simulation_thread.start()
    
    def pause_simulation(self):
        self.paused = not self.paused
        text = "▶️ REANUDAR" if self.paused else "⏸️ PAUSAR"
        self.pause_btn.configure(text=text)
    
    def stop_simulation(self):
        self.running = False
        self.paused = False
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled")
        self.stop_btn.configure(state="disabled")
    
    def run_simulation(self):
        step = 0
        while self.running and (self.scheduler.ready_queue or len(self.scheduler.completed_processes) < len(self.processes)):
            if self.paused:
                time.sleep(0.1)
                continue
            
            step += 1
            process = self.scheduler.get_next_process()
            
            if process:
                self.scheduler.execute_process(process, self.memory, self.filesystem)
                self.update_ui()
                time.sleep(0.5)  # Velocidad de simulación
            else:
                break
        
        self.running = False
        self.root.after(0, lambda: self.start_btn.configure(state="normal"))
        self.root.after(0, lambda: self.pause_btn.configure(state="disabled"))
        self.root.after(0, lambda: self.stop_btn.configure(state="disabled"))
    
    def update_ui(self):
        self.root.after(0, self.update_process_table)
        self.root.after(0, self.update_process_canvas)
        self.root.after(0, self.update_memory_canvas)
        self.root.after(0, self.update_metrics)
        self.root.after(0, self.update_files_log)
    
    def update_process_table(self):
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        all_processes = list(self.scheduler.ready_queue) + self.scheduler.completed_processes
        
        for process in all_processes:
            self.process_tree.insert("", "end", values=(
                process.pid,
                process.state.value,
                process.priority,
                process.burst_time,
                max(0, process.remaining_time),
                f"{process.waiting_time:.2f}"
            ))
    
    def update_process_canvas(self):
        self.process_canvas.delete("all")
        width = self.process_canvas.winfo_width()
        height = 200
        
        if width <= 1:
            width = 800
        
        all_processes = list(self.scheduler.ready_queue) + self.scheduler.completed_processes
        
        if not all_processes:
            return
        
        bar_width = width // len(all_processes) - 5
        x = 10
        
        for process in all_processes:
            progress = (process.burst_time - process.remaining_time) / process.burst_time
            bar_height = int(150 * progress)
            
            color = process.color if process.state != ProcessState.TERMINATED else "#95a5a6"
            
            self.process_canvas.create_rectangle(
                x, height - bar_height - 30, x + bar_width, height - 30,
                fill=color, outline="white", width=2
            )
            
            self.process_canvas.create_text(
                x + bar_width // 2, height - 10,
                text=f"P{process.pid}", fill="white", font=("Arial", 10, "bold")
            )
            
            x += bar_width + 5
    
    def update_memory_canvas(self):
        self.memory_canvas.delete("all")
        width = self.memory_canvas.winfo_width()
        height = self.memory_canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        cols = 5
        rows = (self.memory.num_frames + cols - 1) // cols
        
        cell_width = (width - 40) // cols
        cell_height = (height - 40) // rows
        
        for i, frame in enumerate(self.memory.frames):
            row = i // cols
            col = i % cols
            
            x1 = 20 + col * cell_width
            y1 = 20 + row * cell_height
            x2 = x1 + cell_width - 5
            y2 = y1 + cell_height - 5
            
            color = "#3498db" if frame.page_number is not None else "#34495e"
            
            self.memory_canvas.create_rectangle(
                x1, y1, x2, y2, fill=color, outline="white", width=2
            )
            
            if frame.page_number is not None:
                text = f"P{frame.process_id}\nPg{frame.page_number}"
            else:
                text = "Vacío"
            
            self.memory_canvas.create_text(
                (x1 + x2) // 2, (y1 + y2) // 2,
                text=text, fill="white", font=("Arial", 9, "bold")
            )
    
    def update_metrics(self):
        if not self.scheduler:
            return
        
        metrics = self.scheduler.get_metrics()
        mem_usage = self.memory.get_memory_usage()
        
        text = f"""
Procesos Completados: {metrics['total_processes']}/{len(self.processes)}

Tiempo Promedio Espera:
  {metrics['avg_waiting_time']:.2f} unidades

Tiempo Promedio Retorno:
  {metrics['avg_turnaround_time']:.2f} unidades

Uso de Memoria: {mem_usage:.1f}%

Page Faults: {self.memory.page_faults}
Page Hits: {self.memory.page_hits}

Conflictos de Archivos:
  {self.filesystem.conflicts}
        """
        
        if CTK_AVAILABLE:
            self.metrics_text.delete("0.0", "end")
            self.metrics_text.insert("0.0", text)
        else:
            self.metrics_text.delete("1.0", "end")
            self.metrics_text.insert("1.0", text)
    
    def update_files_log(self):
        if not self.filesystem:
            return
        
        log_text = "REGISTRO DE ACCESO A ARCHIVOS\n"
        log_text += "=" * 50 + "\n\n"
        
        for entry in self.filesystem.access_log[-20:]:
            status_icon = "✅" if entry['status'] == 'SUCCESS' else "❌"
            log_text += f"{status_icon} P{entry['process']} -> {entry['file']} ({entry['mode']}) - {entry['status']}\n"
        
        if CTK_AVAILABLE:
            self.files_text.delete("0.0", "end")
            self.files_text.insert("0.0", log_text)
        else:
            self.files_text.delete("1.0", "end")
            self.files_text.insert("1.0", log_text)
    
    def _generate_processes(self, num: int) -> List[Process]:
        processes = []
        for i in range(num):
            burst_time = random.randint(3, 15)
            process = Process(
                pid=i,
                priority=random.randint(1, 10),
                burst_time=burst_time,
                remaining_time=burst_time,
                arrival_time=0
            )
            processes.append(process)
        return processes
    
    def run(self):
        self.root.mainloop()

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    app = OSSimulatorGUI()
    app.run()

if __name__ == "__main__":
    main()
