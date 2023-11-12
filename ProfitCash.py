import customtkinter as CTk
import sqlite3
import datetime
from tkinter import messagebox
import pandas as pd
from PIL import Image, ImageTk
from openpyxl import Workbook

# Variável global para a janela
janela = None

# Funções
class Conta:
    def __init__(self):
        self.saldo = 0

    def depositar(self, valor):
        self.saldo += valor

    def sacar(self, valor):
        if valor <= self.saldo:
            self.saldo -= valor
        else:
            print("Saldo insuficiente.")

    def obter_saldo(self):
        return self.saldo

# Função para formatar o saldo
def formatar_saldo(saldo):
    saldo_formatado = "R$" + f"{saldo:,.2f}".replace(",", ".")
    return saldo_formatado

def criar_tabela_transacoes():
    conn = sqlite3.connect("transacoes.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY,
        descricao TEXT,
        tipo TEXT,
        valor REAL,
        data_hora TEXT
    )
    """)
    conn.commit()
    conn.close()

def salvar_transacao(descricao, tipo, valor):
    conn = sqlite3.connect("transacoes.db")
    cursor = conn.cursor()
    data_hora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO transacoes (descricao, tipo, valor, data_hora) VALUES (?, ?, ?, ?)", (descricao, tipo, valor, data_hora))
    conn.commit()
    conn.close()

def registrar_transacao(conta, descricao, tipo, saldo_label, entrada_valor):
    valor_text = entrada_valor.get()
    try:
        valor = float(valor_text)
        if tipo == "Depositar":
            conta.depositar(valor)
        elif tipo == "Sacar":
            if valor > conta.obter_saldo():
                messagebox.showerror("Saldo Insuficiente", "Saldo insuficiente para o saque.")
                return
            conta.sacar(valor)
        saldo_label.configure(text=f"Saldo atual: {formatar_saldo(conta.obter_saldo())}")
        salvar_transacao(descricao, tipo, valor)
        print(f"{descricao} ({tipo}): {formatar_saldo(valor)}")
        entrada_valor.delete(0, "end")
    except ValueError:
        print("Valor inválido. Insira um número válido.")

def atualizar_transacoes(text_widget):
    conn = sqlite3.connect("transacoes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transacoes ORDER BY id DESC")
    transacoes = cursor.fetchall()
    transacoes_text = "\n".join([f"{transacao[2]} ({transacao[1]}): {formatar_saldo(transacao[3])} em {transacao[4]}" for transacao in transacoes])


    conn.close()

def sair_sistema():
    global janela
    janela.destroy()

def criar_planilha_com_transacoes():
    conn = sqlite3.connect("transacoes.db")
    df = pd.read_sql_query("SELECT * FROM transacoes", conn)
    conn.close()

    if not df.empty:
        df.to_excel("transacoes.xlsx", index=False)
        messagebox.showinfo("Sucesso", "Planilha de transações criada com sucesso.")
    else:
        messagebox.showinfo("Aviso", "Não há transações para criar a planilha.")


def main():
    global janela

    minha_conta = Conta()
    criar_tabela_transacoes()

    janela = CTk.CTk()
    janela.geometry("1000x500")
    janela.title("ProfitCash")
    janela.iconbitmap('profit.ico')

    tamanho_texto = ("Helvetica", 30)
    tamanho_saldo = ("Helvetica", 30)
    tamanho_ins = ("Helvetica", 25)

    texto = CTk.CTkLabel(janela, text="Sistema de gestão financeira", font=tamanho_texto)
    texto.pack(pady=(janela.winfo_reqheight() - texto.winfo_reqheight()) / 2)
    texto.pack(padx=10, pady=10)

    instrucao = CTk.CTkLabel(janela, text="Escreva o valor abaixo e depois selecione uma das opções.", font=tamanho_ins)
    instrucao.pack(padx='10', pady='10')

    entrada_valor = CTk.CTkEntry(janela, placeholder_text='Digite aqui seu valor')
    entrada_valor.pack(padx=10, pady=10)

    deposito_button = CTk.CTkButton(janela, text="Recebido", fg_color='#04b504', hover_color='#016b01', command=lambda: registrar_transacao(minha_conta, "Depósito", "Depositar", saldo_label, entrada_valor))
    deposito_button.pack(padx=10, pady=10)

    saque_button = CTk.CTkButton(janela, text="Pago", fg_color='#b50404', hover_color='#4f0101', command=lambda: registrar_transacao(minha_conta, "Saque", "Sacar", saldo_label, entrada_valor))
    saque_button.pack(padx=10, pady=10)

    planilha_button = CTk.CTkButton(janela, text="Gerar Planilha", command=criar_planilha_com_transacoes, fg_color='#00918a', hover_color='#01403d')
    planilha_button.pack(padx=10, pady=10)

    sair_button = CTk.CTkButton(janela, text="Sair do sistema", command=sair_sistema)
    sair_button.pack(padx='10', pady='10')

    saldo_label = CTk.CTkLabel(janela, text=f"Saldo atual: {formatar_saldo(minha_conta.obter_saldo())}", font=tamanho_saldo, text_color='black', bg_color='gray')
    saldo_label.pack(side="bottom", anchor="se", padx=10, pady=10)

    frame_lista = CTk.CTkFrame(janela)
    frame_lista.pack(side="bottom", anchor="sw", padx=10, pady=10, fill="both", expand=True)


    janela.mainloop()

if __name__ == "__main__":
    main()
