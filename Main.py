import tkinter as tk
from tkinter import ttk, messagebox

# ============================================================
# === FUNCIONES DE UTILIDAD =================================
# ============================================================

def parse_matrix_text(text):
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if not lines:
        raise ValueError("Entrada vacía. Ingrese una matriz.")
    matrix = []
    num_cols = None
    for i, line in enumerate(lines, start=1):
        parts = line.split()
        row = []
        for j, token in enumerate(parts, start=1):
            try:
                v = float(token)
            except ValueError:
                raise ValueError(f"Valor no numérico en línea {i}, columna {j}: '{token}'")
            row.append(v)
        if num_cols is None:
            num_cols = len(row)
        elif len(row) != num_cols:
            raise ValueError(f"Filas de longitud inconsistente en línea {i}.")
        matrix.append(row)
    return matrix

def matrix_to_text(matrix, tol=1e-12):
    lines = []
    for row in matrix:
        parts = []
        for x in row:
            if abs(round(x) - x) < tol:
                parts.append(str(int(round(x))))
            else:
                parts.append(f"{x:.6f}".rstrip('0').rstrip('.'))
        lines.append("  ".join(parts))
    return "\n".join(lines)

def imprimir_matriz_text(matriz, titulo="Matriz:"):
    s = f"\n{titulo}\n"
    for fila in matriz:
        s += "  ".join(f"{val:10.6f}" for val in fila) + "\n"
    s += "\n"
    return s

def multiply_matrices_step(a, b):
    if len(a[0]) != len(b):
        raise ValueError("Número de columnas de A debe igualar número de filas de B para multiplicar.")
    rows, cols, inner = len(a), len(b[0]), len(b)
    result = [[0.0 for _ in range(cols)] for _ in range(rows)]
    salida = ""
    for i in range(rows):
        for j in range(cols):
            salida += f"Calculando elemento ({i+1},{j+1}): "
            total = 0.0
            for k in range(inner):
                salida += f"{a[i][k]:.3f}*{b[k][j]:.3f}"
                total += a[i][k]*b[k][j]
                if k < inner-1:
                    salida += " + "
            salida += f" = {total:.6f}\n"
            result[i][j] = total
    salida += "\nResultado de la multiplicación:\n"
    salida += matrix_to_text(result)
    return salida, result

# ============================================================
# === FUNCION PRINCIPAL: INVERSA DE MATRIZ ==================
# ============================================================

def invertir_matriz_pasoa_paso(A, tol=1e-12):
    n = len(A)
    if n == 0:
        raise ValueError("La matriz no puede estar vacía.")
    if any(len(fila) != n for fila in A):
        raise ValueError("La matriz debe ser cuadrada.")

    M = [A[i][:] + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    salida = imprimir_matriz_text(M, "Matriz aumentada [A | I] inicial:")

    for i in range(n):
        max_fila = i
        for k in range(i + 1, n):
            if abs(M[k][i]) > abs(M[max_fila][i]):
                max_fila = k
        if abs(M[max_fila][i]) < tol:
            raise ValueError("La matriz es singular y no tiene inversa (pivote nulo).")

        if max_fila != i:
            M[i], M[max_fila] = M[max_fila], M[i]
            salida += f"Intercambio fila {i+1} ↔ fila {max_fila+1}\n"
            salida += imprimir_matriz_text(M, f"Después del intercambio en columna {i+1}:")

        pivote = M[i][i]
        salida += f"Normalizando fila {i+1} (dividir por {pivote:.6f})\n"
        for j in range(2 * n):
            M[i][j] /= pivote
        salida += imprimir_matriz_text(M, f"Después de normalizar fila {i+1}:")

        for k in range(n):
            if k != i:
                factor = M[k][i]
                if abs(factor) > tol:
                    salida += f"Eliminando columna {i+1} en fila {k+1} (factor {factor:.6f})\n"
                    for j in range(2 * n):
                        M[k][j] -= factor * M[i][j]
                    salida += imprimir_matriz_text(M, f"Después de eliminar en fila {k+1}:")

    inversa = [fila[n:] for fila in M]
    salida += imprimir_matriz_text(M, "Matriz reducida final [I | A⁻¹]:")
    salida += "\n✅ Inversa de A (derecha de la matriz aumentada):\n"
    salida += matrix_to_text(inversa) + "\n"

    salida += "\n🔹 Comprobación: A * A⁻¹ (debe dar identidad)\n"
    mult_texto, mult_result = multiply_matrices_step(A, inversa)
    salida += mult_texto + "\n"

    identidad = [[1.0 if i==j else 0.0 for j in range(n)] for i in range(n)]
    es_identidad = all(abs(mult_result[i][j]-identidad[i][j])<tol for i in range(n) for j in range(n))
    salida += "✅ Comprobación final: "
    salida += "Correcta (producto ≈ identidad)\n" if es_identidad else "Incorrecta (producto no es identidad)\n"

    return salida

# ============================================================
# === INTERFAZ GRÁFICA =====================================
# ============================================================

class AppInversa:
    def __init__(self, root):
        self.root = root
        self.root.title("Inversión de Matriz con Verificación")
        self.root.geometry("950x700")
        self.root.configure(padx=10, pady=10)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1)

        ttk.Label(root, text="Ingrese la matriz cuadrada:", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")

        # Cuadro con scroll para entrada
        entrada_frame = ttk.Frame(root)
        entrada_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        entrada_scroll = tk.Scrollbar(entrada_frame)
        entrada_scroll.pack(side="right", fill="y")
        self.txt = tk.Text(entrada_frame, width=100, height=8, yscrollcommand=entrada_scroll.set)
        self.txt.pack(side="left", fill="both", expand=True)
        entrada_scroll.config(command=self.txt.yview)

        ttk.Label(root, text="Resultado paso a paso:", font=("Segoe UI", 12, "bold")).grid(row=2, column=0, sticky="w")

        # Cuadro con scroll para resultados
        resultado_frame = ttk.Frame(root)
        resultado_frame.grid(row=3, column=0, sticky="nsew", pady=5)
        resultado_scroll = tk.Scrollbar(resultado_frame)
        resultado_scroll.pack(side="right", fill="y")
        self.res = tk.Text(resultado_frame, width=100, height=25, yscrollcommand=resultado_scroll.set)
        self.res.pack(side="left", fill="both", expand=True)
        resultado_scroll.config(command=self.res.yview)

        # Botones
        botones_frame = ttk.Frame(root)
        botones_frame.grid(row=4, column=0, pady=10)
        ttk.Button(botones_frame, text="Calcular Inversa y Verificar", command=self.calcular_inversa).pack(side="left", padx=10)
        ttk.Button(botones_frame, text="Salir", command=root.destroy).pack(side="left", padx=10)

    def calcular_inversa(self):
        self.res.delete("1.0", tk.END)
        try:
            matriz = parse_matrix_text(self.txt.get("1.0", tk.END))
            pasos = invertir_matriz_pasoa_paso([fila[:] for fila in matriz])
            self.res.insert(tk.END, pasos)
        except Exception as e:
            messagebox.showerror("Error", str(e))

# ============================================================
# === EJECUCIÓN PRINCIPAL ===================================
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = AppInversa(root)
    root.mainloop()
