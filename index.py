import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta, date
import calendar

class RestauranteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Tortas")

        self.tamanhos = ["P", "M", "G", "GG"]
        self.preco_tamanhos = {"P": 50, "M": 70, "G": 90, "GG": 120}

        self.create_input_fields()
        self.create_generate_button()

    def create_input_fields(self):
        tk.Label(self.root, text="Tamanho da Torta:").grid(row=0, column=0, padx=10, pady=10)
        self.tamanho_var = tk.StringVar()
        tamanho_combobox = ttk.Combobox(self.root, textvariable=self.tamanho_var, values=self.tamanhos)
        tamanho_combobox.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Quantidade:").grid(row=1, column=0, padx=10, pady=10)
        self.quantidade_entry = tk.Entry(self.root)
        self.quantidade_entry.grid(row=1, column=1, padx=10, pady=10)

    def create_generate_button(self):
        generate_button = tk.Button(self.root, text="Lançar Pedido", command=self.add_to_spreadsheet)
        generate_button.grid(row=2, column=0, columnspan=2, pady=10)

        generate_planilha_button = tk.Button(self.root, text="Gerar Planilha", command=self.generate_spreadsheet)
        generate_planilha_button.grid(row=3, column=0, columnspan=2, pady=10)

    def add_to_spreadsheet(self):
        tamanho = self.tamanho_var.get()
        quantidade = int(self.quantidade_entry.get())

        if tamanho not in self.tamanhos:
            messagebox.showerror("Erro", "Tamanho inválido.")
            return

        try:
            df = pd.read_csv("planilha_tortas.csv")
        except FileNotFoundError:
            df = self.create_empty_dataframe()

        # Obter a data atual
        data_atual = datetime.now()

        # Verificar se é o dia específico da semana para o lançamento (por exemplo, segunda-feira)
        if data_atual.weekday() != 0:  # 0 corresponde a segunda-feira
            messagebox.showinfo("Informação", "Lançamentos permitidos apenas às segundas-feiras.")
            return

        # Verificar se já existe um registro para o dia atual
        if len(df) > 0 and df["Dia"].iloc[-1] == data_atual.strftime("%Y-%m-%d"):
            # Adicionar a quantidade ao registro existente
            df.loc[df.index[-1], tamanho] += quantidade
        else:
            # Criar um novo registro para o dia atual
            new_row = {"Dia": data_atual.strftime("%Y-%m-%d"), tamanho: quantidade}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        # Calcular o valor total considerando a precificação
        for tamanho in self.tamanhos:
            df[tamanho] = df[tamanho].fillna(0)
        df["Total"] = df.apply(lambda row: sum(row[tamanho] * self.preco_tamanhos[tamanho] for tamanho in self.tamanhos), axis=1)

        df.to_csv("planilha_tortas.csv", index=False)
        messagebox.showinfo("Sucesso", "Pedido lançado com sucesso.")

        # Limpar os campos após o lançamento
        self.tamanho_var.set("")
        self.quantidade_entry.delete(0, tk.END)

    def generate_spreadsheet(self):
        try:
            df = pd.read_csv("planilha_tortas.csv")
        except FileNotFoundError:
            messagebox.showerror("Erro", "Nenhum pedido registrado para gerar a planilha.")
            return

        df.to_csv("planilha_tortas_gerada.csv", index=False)
        messagebox.showinfo("Sucesso", "Planilha gerada com sucesso.")

    def create_empty_dataframe(self):
        # Obter o último dia do mês
        last_day = date.today().replace(day=28) + timedelta(days=4)
        last_day = last_day - timedelta(days=last_day.day)
        
        # Criar um DataFrame vazio com as colunas necessárias
        df = pd.DataFrame(columns=["Dia"] + self.tamanhos + ["Total"])

        # Adicionar linhas para cada dia do mês
        for day in range(1, last_day.day + 1):
            date_str = f"{datetime.now().year}-{datetime.now().month:02d}-{day:02d}"
            new_row = {"Dia": date_str}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        return df

if __name__ == "__main__":
    root = tk.Tk()
    app = RestauranteApp(root)
    root.mainloop()
