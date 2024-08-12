import os
from dotenv import load_dotenv
import psycopg2
from tkinter import *
from tkinter import messagebox, filedialog, ttk
from tkcalendar import Calendar, DateEntry
from decimal import Decimal, InvalidOperation
import locale
import csv
import xml.etree.ElementTree as ET
from fpdf import FPDF
from datetime import datetime, timedelta
import bcrypt

load_dotenv()

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def conectar_bd():
    try:
        conn = psycopg2.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME')
        )
        print("Conexão ao banco de dados realizada com sucesso!")
        return conn
    except Exception as error:
        print(f"Erro ao conectar ao banco de dados: {error}")
        messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {error}")
        return None

def criar_tabelas():
    conn = conectar_bd()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL
                );
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    telefone VARCHAR(20),
                    usuario_id INTEGER NOT NULL,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
                );
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pagamentos (
                    id SERIAL PRIMARY KEY,
                    cliente_id INTEGER NOT NULL,
                    tipo_pagamento VARCHAR(50) NOT NULL,
                    valor DECIMAL(10, 2) NOT NULL,
                    data_pagamento DATE NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    usuario_id INTEGER NOT NULL,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
                );
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projetos (
                    id SERIAL PRIMARY KEY,
                    cliente_id INTEGER NOT NULL,
                    nome_projeto VARCHAR(255) NOT NULL,
                    tipo_projeto VARCHAR(50) NOT NULL,
                    valor DECIMAL(10, 2) NOT NULL,
                    data_entrega DATE NOT NULL,
                    recorrente BOOLEAN NOT NULL DEFAULT FALSE,
                    usuario_id INTEGER NOT NULL,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
                );
            ''')

            conn.commit()
            print("Tabelas 'usuarios', 'clientes', 'pagamentos' e 'projetos' criadas ou já existentes.")
        except Exception as error:
            print(f"Erro ao criar tabelas: {error}")
        finally:
            conn.close()
    else:
        print("Erro ao conectar ao banco de dados para criar tabelas.")

def verificar_login(username, password):
    conn = conectar_bd()
    if conn:
        cursor = conn.cursor()
        print(f"Verificando usuário: {username}")
        cursor.execute("SELECT id, password FROM usuarios WHERE username=%s", (username,))
        user = cursor.fetchone()
        conn.close()

        if user:
            print(f"Usuário encontrado: {user[0]}, {user[1]}")
            if bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
                return user[0]
        return None

def registrar_usuario(username, password):
    conn = conectar_bd()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
        if cursor.fetchone():
            messagebox.showerror("Erro", "Nome de usuário já existe.")
            return
    
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        conn.close()
        print("Usuário registrado com sucesso!")

def cadastrar_cliente(nome, email, telefone, usuario_id):
    conn = conectar_bd()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clientes (nome, email, telefone, usuario_id) VALUES (%s, %s, %s, %s)", (nome, email, telefone, usuario_id))
        conn.commit()
        conn.close()

def editar_cliente(cliente_id, nome, email, telefone, usuario_id):
    conn = conectar_bd()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''UPDATE clientes SET nome=%s, email=%s, telefone=%s WHERE id=%s AND usuario_id=%s''', 
                       (nome, email, telefone, cliente_id, usuario_id))
        conn.commit()
        conn.close()

def excluir_cliente(cliente_id, usuario_id):
    conn = conectar_bd()
    if conn:
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM pagamentos WHERE cliente_id=%s AND usuario_id=%s", (cliente_id, usuario_id))
            cursor.execute("DELETE FROM projetos WHERE cliente_id=%s AND usuario_id=%s", (cliente_id, usuario_id))
            cursor.execute("DELETE FROM clientes WHERE id=%s AND usuario_id=%s", (cliente_id, usuario_id))
            conn.commit()
            messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Erro ao excluir cliente: {e}")
        finally:
            conn.close()

def cadastrar_pagamento(cliente_id, tipo_pagamento, valor, data_pagamento, status, usuario_id):
    conn = conectar_bd()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO pagamentos (cliente_id, tipo_pagamento, valor, data_pagamento, status, usuario_id) 
                          VALUES (%s, %s, %s, %s, %s, %s)''', (cliente_id, tipo_pagamento, valor, data_pagamento, status, usuario_id))
        conn.commit()
        conn.close()

def editar_pagamento(pagamento_id, tipo_pagamento, valor, data_pagamento, status, usuario_id):
    conn = conectar_bd()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''UPDATE pagamentos SET tipo_pagamento=%s, valor=%s, data_pagamento=%s, status=%s 
                          WHERE id=%s AND usuario_id=%s''', (tipo_pagamento, valor, data_pagamento, status, pagamento_id, usuario_id))
        conn.commit()
        conn.close()

def excluir_pagamento(pagamento_id, usuario_id):
    conn = conectar_bd()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pagamentos WHERE id=%s AND usuario_id=%s", (pagamento_id, usuario_id))
        conn.commit()
        conn.close()

def cadastrar_projeto(cliente_id, nome_projeto, tipo_projeto, valor, data_entrega, recorrente, usuario_id):
    conn = conectar_bd()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO projetos (cliente_id, nome_projeto, tipo_projeto, valor, data_entrega, recorrente, usuario_id) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s)''', (cliente_id, nome_projeto, tipo_projeto, valor, data_entrega, recorrente, usuario_id))
        conn.commit()
        conn.close()

def editar_projeto(projeto_id, nome_projeto, tipo_projeto, valor, data_entrega, recorrente, usuario_id):
    conn = conectar_bd()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''UPDATE projetos SET nome_projeto=%s, tipo_projeto=%s, valor=%s, data_entrega=%s, recorrente=%s 
                          WHERE id=%s AND usuario_id=%s''', (nome_projeto, tipo_projeto, valor, data_entrega, recorrente, projeto_id, usuario_id))
        conn.commit()
        conn.close()

def excluir_projeto(projeto_id, usuario_id):
    conn = conectar_bd()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM projetos WHERE id=%s AND usuario_id=%s", (projeto_id, usuario_id))
        conn.commit()
        conn.close()

def verificar_alertas(usuario_id):
    conn = conectar_bd()
    if conn:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT clientes.nome, pagamentos.tipo_pagamento, pagamentos.valor, TO_CHAR(pagamentos.data_pagamento, 'DD-MM-YYYY')
            FROM pagamentos
            JOIN clientes ON pagamentos.cliente_id = clientes.id
            WHERE pagamentos.status = 'Em Aberto'
            AND pagamentos.data_pagamento <= CURRENT_DATE + INTERVAL '7 days'
            AND pagamentos.usuario_id = %s
        ''', (usuario_id,))
        pagamentos_pendentes = cursor.fetchall()

        if pagamentos_pendentes:
            alerta_pagamentos = "Pagamentos próximos do vencimento:\n"
            for pagamento in pagamentos_pendentes:
                alerta_pagamentos += f"Cliente: {pagamento[0]}, Tipo: {pagamento[1]}, Valor: {pagamento[2]}, Data: {pagamento[3]}\n"
            messagebox.showwarning("Alertas de Pagamentos", alerta_pagamentos)

        cursor.execute('''
            SELECT clientes.nome, projetos.nome_projeto, TO_CHAR(projetos.data_entrega, 'DD-MM-YYYY')
            FROM projetos
            JOIN clientes ON projetos.cliente_id = clientes.id
            WHERE projetos.data_entrega <= CURRENT_DATE + INTERVAL '7 days'
            AND projetos.usuario_id = %s
        ''', (usuario_id,))
        projetos_proximos = cursor.fetchall()

        if projetos_proximos:
            alerta_projetos = "Projetos com entrega próxima:\n"
            for projeto in projetos_proximos:
                alerta_projetos += f"Cliente: {projeto[0]}, Projeto: {projeto[1]}, Data de Entrega: {projeto[2]}\n"
            messagebox.showwarning("Alertas de Projetos", alerta_projetos)

        conn.close()

def carregar_projetos(usuario_id):
    conn = conectar_bd()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT clientes.nome, projetos.nome_projeto, TO_CHAR(projetos.data_entrega, 'DD-MM-YYYY'), projetos.recorrente, projetos.id
            FROM projetos
            JOIN clientes ON projetos.cliente_id = clientes.id
            WHERE projetos.usuario_id = %s
            ORDER BY projetos.data_entrega
        ''', (usuario_id,))
        projetos = cursor.fetchall()
        conn.close()
        return projetos

def exportar_csv(dados, filepath):
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Cliente ID", "Nome", "Email", "Telefone", "Pagamento ID", "Tipo de Pagamento", "Valor", "Data", "Status"])
        writer.writerows(dados)

def exportar_xml(dados, filepath):
    root = ET.Element("Clientes")
    for row in dados:
        cliente = ET.SubElement(root, "Cliente")
        ET.SubElement(cliente, "ClienteID").text = str(row[0])
        ET.SubElement(cliente, "Nome").text = row[1]
        ET.SubElement(cliente, "Email").text = row[2]
        ET.SubElement(cliente, "Telefone").text = row[3]
        pagamento = ET.SubElement(cliente, "Pagamento")
        ET.SubElement(pagamento, "PagamentoID").text = str(row[4])
        ET.SubElement(pagamento, "TipoPagamento").text = row[5]
        ET.SubElement(pagamento, "Valor").text = str(row[6])
        ET.SubElement(pagamento, "Data").text = row[7]
        ET.SubElement(pagamento, "Status").text = row[8]
    
    tree = ET.ElementTree(root)
    tree.write(filepath, encoding='utf-8', xml_declaration=True)

def exportar_pdf(dados, filepath):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Relatório de Clientes e Pagamentos", ln=True, align='C')
    pdf.ln(10)

    for row in dados:
        pdf.cell(0, 10, txt=f"Cliente ID: {row[0]}, Nome: {row[1]}, Email: {row[2]}, Telefone: {row[3]}", ln=True)
        pdf.cell(0, 10, txt=f"Pagamento ID: {row[4]}, Tipo: {row[5]}, Valor: R$ {row[6]}, Data: {row[7]}, Status: {row[8]}", ln=True)
        pdf.ln(5)

    pdf.output(filepath)


class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gerenciamento de Clientes")
        self.root.state('zoomed')  
        self.usuario_id = None  

        self.login_frame = Frame(root)
        self.login_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        Label(self.login_frame, text="Usuário", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10)
        Label(self.login_frame, text="Senha", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10)

        self.username_entry = Entry(self.login_frame, font=("Arial", 14))
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        self.password_entry = Entry(self.login_frame, show="*", font=("Arial", 14))
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        Button(self.login_frame, text="Login", command=self.login, font=("Arial", 14)).grid(row=2, column=0, columnspan=2, pady=10)
        Button(self.login_frame, text="Registrar", command=self.show_register, font=("Arial", 14)).grid(row=3, column=0, columnspan=2, pady=10)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Erro", "Por favor, preencha ambos os campos: Usuário e Senha.")
            return

        user_id = verificar_login(username, password)
        if user_id:
            self.usuario_id = user_id  
            self.login_frame.place_forget()  
            self.show_menu()
            verificar_alertas(self.usuario_id)  
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos")

    def show_register(self):
        self.login_frame.pack_forget()
        self.register_frame = Frame(self.root)
        self.register_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        Label(self.register_frame, text="Novo Usuário", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10)
        Label(self.register_frame, text="Senha", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10)

        self.new_username_entry = Entry(self.register_frame, font=("Arial", 14))
        self.new_username_entry.grid(row=0, column=1, padx=10, pady=10)

        self.new_password_entry = Entry(self.register_frame, show="*", font=("Arial", 14))
        self.new_password_entry.grid(row=1, column=1, padx=10, pady=10)

        Button(self.register_frame, text="Registrar", command=self.register, font=("Arial", 14)).grid(row=2, column=0, columnspan=2, pady=10)
        Button(self.register_frame, text="Voltar", command=self.show_login, font=("Arial", 14)).grid(row=3, column=0, columnspan=2, pady=10)

    def register(self):
        username = self.new_username_entry.get().strip()
        password = self.new_password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Erro", "Por favor, preencha ambos os campos: Usuário e Senha.")
            return

        registrar_usuario(username, password)
        messagebox.showinfo("Sucesso", "Usuário registrado com sucesso!")
        self.show_login()

    def show_login(self):
        if hasattr(self, 'register_frame'):
            self.register_frame.place_forget()  
        if hasattr(self, 'menu_frame'):
            self.menu_frame.pack_forget()  
        self.login_frame.place(relx=0.5, rely=0.5, anchor=CENTER)  

    def show_menu(self):
        if hasattr(self, 'menu_frame'):
            self.menu_frame.pack_forget()  
        if hasattr(self, 'projetos_frame'):
            self.projetos_frame.pack_forget()  
        if hasattr(self, 'cadastrar_cliente_frame'):
            self.cadastrar_cliente_frame.place_forget()  

        self.menu_frame = Frame(self.root)
        self.menu_frame.pack(side=TOP, fill=X)

        Button(self.menu_frame, text="Cadastrar Cliente", command=self.show_cadastrar_cliente, font=("Arial", 12)).pack(side=LEFT, padx=10, pady=10)
        Button(self.menu_frame, text="Cadastrar Pagamento", command=self.show_cadastrar_pagamento, font=("Arial", 12)).pack(side=LEFT, padx=10, pady=10)
        Button(self.menu_frame, text="Ver Clientes e Pagamentos", command=self.show_clientes_pagamentos, font=("Arial", 12)).pack(side=LEFT, padx=10, pady=10)
        Button(self.menu_frame, text="Gerar Relatórios", command=self.show_relatorios, font=("Arial", 12)).pack(side=LEFT, padx=10, pady=10)
        Button(self.menu_frame, text="Cadastrar Projeto", command=self.show_cadastrar_projeto, font=("Arial", 12)).pack(side=LEFT, padx=10, pady=10)
        Button(self.menu_frame, text="Sair", command=self.logout, font=("Arial", 12)).pack(side=RIGHT, padx=10, pady=10)
        
        self.mostrar_projetos_cadastrados()  

    def mostrar_projetos_cadastrados(self):
       
        self.projetos_frame = Frame(self.root)
        self.projetos_frame.pack(fill=BOTH, expand=True)

        self.tree = ttk.Treeview(self.projetos_frame, columns=("Cliente", "Projeto", "Data de Entrega", "Recorrente", "ID do Projeto"), show="headings")
        self.tree.heading("Cliente", text="Cliente")
        self.tree.heading("Projeto", text="Projeto")
        self.tree.heading("Data de Entrega", text="Data de Entrega")
        self.tree.heading("Recorrente", text="Recorrente")
        self.tree.heading("ID do Projeto", text="ID do Projeto") 

        self.tree.pack(fill=BOTH, expand=True)

        self.tree.delete(*self.tree.get_children())

        projetos = carregar_projetos(self.usuario_id)
        if projetos:
            for projeto in projetos:
                recorrente_texto = "Mensal" if projeto[3] else "Único"
                self.tree.insert("", END, values=(projeto[0], projeto[1], projeto[2], recorrente_texto, projeto[4]))

        self.btn_editar_projeto = Button(self.projetos_frame, text="Editar Projeto", command=self.editar_projeto, font=("Arial", 12))
        self.btn_editar_projeto.pack(side=LEFT, padx=10, pady=10)

        self.btn_excluir_projeto = Button(self.projetos_frame, text="Excluir Projeto", command=self.excluir_projeto, font=("Arial", 12))
        self.btn_excluir_projeto.pack(side=LEFT, padx=10, pady=10)

    def logout(self):
        if hasattr(self, 'projetos_frame'):
            self.projetos_frame.pack_forget()  
        self.show_login()

    def show_cadastrar_cliente(self):
        self.menu_frame.pack_forget()
        if hasattr(self, 'projetos_frame'):
            self.projetos_frame.pack_forget()  

        self.cadastrar_cliente_frame = Frame(self.root)
        self.cadastrar_cliente_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        Label(self.cadastrar_cliente_frame, text="Cadastrar Cliente", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=10)

        Label(self.cadastrar_cliente_frame, text="Nome", font=("Arial", 12)).grid(row=1, column=0, pady=5, sticky=E)
        Label(self.cadastrar_cliente_frame, text="Email", font=("Arial", 12)).grid(row=2, column=0, pady=5, sticky=E)
        Label(self.cadastrar_cliente_frame, text="Telefone", font=("Arial", 12)).grid(row=3, column=0, pady=5, sticky=E)

        self.cliente_nome_entry = Entry(self.cadastrar_cliente_frame, font=("Arial", 12))
        self.cliente_nome_entry.grid(row=1, column=1, pady=5)

        self.cliente_email_entry = Entry(self.cadastrar_cliente_frame, font=("Arial", 12))
        self.cliente_email_entry.grid(row=2, column=1, pady=5)

        self.cliente_telefone_entry = Entry(self.cadastrar_cliente_frame, font=("Arial", 12))
        self.cliente_telefone_entry.grid(row=3, column=1, pady=5)

        Button(self.cadastrar_cliente_frame, text="Salvar", command=self.salvar_cliente, font=("Arial", 12)).grid(row=4, column=0, columnspan=2, pady=10)
        Button(self.cadastrar_cliente_frame, text="Voltar", command=self.show_menu_from_cliente, font=("Arial", 12)).grid(row=5, column=0, columnspan=2, pady=10)

    def salvar_cliente(self):
        nome = self.cliente_nome_entry.get()
        email = self.cliente_email_entry.get()
        telefone = self.cliente_telefone_entry.get()
        cadastrar_cliente(nome, email, telefone, self.usuario_id)
        messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
        self.cliente_nome_entry.delete(0, END)
        self.cliente_email_entry.delete(0, END)
        self.cliente_telefone_entry.delete(0, END)

    def show_menu_from_cliente(self):
        self.cadastrar_cliente_frame.place_forget()
        self.show_menu()

    def show_cadastrar_pagamento(self):
        self.menu_frame.pack_forget()
        if hasattr(self, 'projetos_frame'):
            self.projetos_frame.pack_forget()  

        self.cadastrar_pagamento_frame = Frame(self.root)
        self.cadastrar_pagamento_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        Label(self.cadastrar_pagamento_frame, text="Cadastrar Pagamento", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=10)

        Label(self.cadastrar_pagamento_frame, text="Cliente", font=("Arial", 12)).grid(row=1, column=0, sticky=E, pady=5)
        self.pagamento_cliente_id_combobox = ttk.Combobox(self.cadastrar_pagamento_frame, font=("Arial", 12))
        self.pagamento_cliente_id_combobox.grid(row=1, column=1, pady=5)
        self.carregar_clientes()

        Label(self.cadastrar_pagamento_frame, text="Tipo de Pagamento", font=("Arial", 12)).grid(row=2, column=0, sticky=E, pady=5)
        self.pagamento_tipo_combobox = ttk.Combobox(self.cadastrar_pagamento_frame, font=("Arial", 12), values=[
            'PIX', 'Cartão de Débito', 'Cartão de Crédito', 'Dinheiro'
        ])
        self.pagamento_tipo_combobox.grid(row=2, column=1, pady=5)

        Label(self.cadastrar_pagamento_frame, text="Valor (R$)", font=("Arial", 12)).grid(row=3, column=0, sticky=E, pady=5)
        self.pagamento_valor_entry = Entry(self.cadastrar_pagamento_frame, font=("Arial", 12))
        self.pagamento_valor_entry.grid(row=3, column=1, pady=5)
        self.pagamento_valor_entry.bind('<FocusOut>', self.formatar_valor)

        Label(self.cadastrar_pagamento_frame, text="Data de Pagamento", font=("Arial", 12)).grid(row=4, column=0, sticky=E, pady=5)
        self.pagamento_data_entry = Entry(self.cadastrar_pagamento_frame, font=("Arial", 12))
        self.pagamento_data_entry.grid(row=4, column=1, pady=5)

        Button(self.cadastrar_pagamento_frame, text="Selecionar Data", command=self.mostrar_calendario, font=("Arial", 12)).grid(row=4, column=2, pady=5, padx=5)

        Label(self.cadastrar_pagamento_frame, text="Status", font=("Arial", 12)).grid(row=5, column=0, sticky=E, pady=5)
        self.pagamento_status_combobox = ttk.Combobox(self.cadastrar_pagamento_frame, font=("Arial", 12), values=[
            'Pago', 'Em Aberto'
        ])
        self.pagamento_status_combobox.grid(row=5, column=1, pady=5)

        Button(self.cadastrar_pagamento_frame, text="Salvar", command=self.salvar_pagamento, font=("Arial", 12)).grid(row=6, column=0, columnspan=2, pady=10)
        Button(self.cadastrar_pagamento_frame, text="Voltar", command=self.show_menu_from_pagamento, font=("Arial", 12)).grid(row=7, column=0, columnspan=2, pady=10)

    def mostrar_calendario(self):
        self.calendario_toplevel = Toplevel(self.root)
        self.calendario = Calendar(self.calendario_toplevel, date_pattern='dd-mm-yyyy')
        self.calendario.pack()
        Button(self.calendario_toplevel, text="Selecionar", command=self.selecionar_data).pack()

    def selecionar_data(self):
        self.pagamento_data_entry.delete(0, END)
        self.pagamento_data_entry.insert(0, self.calendario.get_date())
        self.calendario_toplevel.destroy()

    def carregar_clientes(self):
        conn = conectar_bd()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome FROM clientes WHERE usuario_id=%s", (self.usuario_id,))
            clientes = cursor.fetchall()
            self.pagamento_cliente_id_combobox['values'] = [f"{cliente[0]} - {cliente[1]}" for cliente in clientes]
            conn.close()

    def formatar_valor(self, event):
        try:
            valor = Decimal(self.pagamento_valor_entry.get().replace('R$', '').replace('.', '').replace(',', '.'))
            self.pagamento_valor_entry.delete(0, END)
            self.pagamento_valor_entry.insert(0, locale.currency(valor, grouping=True))
        except InvalidOperation:
            messagebox.showerror("Erro", "Valor inválido!")

    def salvar_pagamento(self):
        cliente_id = int(self.pagamento_cliente_id_combobox.get().split(' - ')[0])
        tipo_pagamento = self.pagamento_tipo_combobox.get()
        valor = Decimal(self.pagamento_valor_entry.get().replace('R$', '').replace('.', '').replace(',', '.'))
        data_pagamento = self.pagamento_data_entry.get()
        status = self.pagamento_status_combobox.get()
        cadastrar_pagamento(cliente_id, tipo_pagamento, valor, data_pagamento, status, self.usuario_id)
        messagebox.showinfo("Sucesso", "Pagamento cadastrado com sucesso!")
        self.pagamento_cliente_id_combobox.set('')
        self.pagamento_tipo_combobox.set('')
        self.pagamento_valor_entry.delete(0, END)
        self.pagamento_data_entry.delete(0, END)
        self.pagamento_status_combobox.set('')

    def show_menu_from_pagamento(self):
        self.cadastrar_pagamento_frame.place_forget()
        self.show_menu()

    def show_clientes_pagamentos(self):
        self.menu_frame.pack_forget()
        if hasattr(self, 'projetos_frame'):
            self.projetos_frame.pack_forget()  

        self.clientes_pagamentos_frame = Frame(self.root)
        self.clientes_pagamentos_frame.pack(fill=BOTH, expand=True)

        self.clientes_pagamentos_buttons_frame = Frame(self.root)
        self.clientes_pagamentos_buttons_frame.pack(side=TOP, fill=X)

        Button(self.clientes_pagamentos_buttons_frame, text="Editar Cliente", command=self.editar_cliente, font=("Arial", 12)).pack(side=LEFT, padx=10, pady=10)
        Button(self.clientes_pagamentos_buttons_frame, text="Excluir Cliente", command=self.excluir_cliente, font=("Arial", 12)).pack(side=LEFT, padx=10, pady=10)
        Button(self.clientes_pagamentos_buttons_frame, text="Voltar", command=self.show_menu_from_clientes_pagamentos).pack(side=RIGHT, pady=10)

        self.tree = ttk.Treeview(self.clientes_pagamentos_frame, columns=(
            "Cliente ID", "Nome", "Email", "Telefone"), show="headings")
        self.tree.heading("Cliente ID", text="Cliente ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Telefone", text="Telefone")
        self.tree.pack(side=LEFT, fill=Y)

        self.carregar_clientes_pagamentos()

        self.detalhes_frame = Frame(self.clientes_pagamentos_frame)
        self.detalhes_frame.pack(side=LEFT, fill=BOTH, expand=True)

        self.detalhes_tree = ttk.Treeview(self.detalhes_frame, columns=(
            "Pagamento ID", "Tipo de Pagamento", "Valor", "Data", "Status"), show="headings")
        self.detalhes_tree.heading("Pagamento ID", text="Pagamento ID")
        self.detalhes_tree.heading("Tipo de Pagamento", text="Tipo de Pagamento")
        self.detalhes_tree.heading("Valor", text="Valor (R$)")
        self.detalhes_tree.heading("Data", text="Data de Pagamento")
        self.detalhes_tree.heading("Status", text="Status")
        self.detalhes_tree.pack(fill=BOTH, expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.mostrar_detalhes_pagamentos)

        Button(self.detalhes_frame, text="Editar Pagamento", command=self.editar_pagamento, font=("Arial", 12)).pack(side=LEFT, padx=10, pady=10)
        Button(self.detalhes_frame, text="Excluir Pagamento", command=self.excluir_pagamento, font=("Arial", 12)).pack(side=LEFT, padx=10, pady=10)

    def carregar_clientes_pagamentos(self):
        conn = conectar_bd()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, email, telefone FROM clientes WHERE usuario_id=%s", (self.usuario_id,))
            clientes = cursor.fetchall()
            for cliente in clientes:
                self.tree.insert("", END, values=cliente)
            self.clientes = clientes
            conn.close()

    def mostrar_detalhes_pagamentos(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        cliente_id = self.tree.item(selected_item[0], "values")[0]

        self.detalhes_tree.delete(*self.detalhes_tree.get_children())  

        conn = conectar_bd()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, tipo_pagamento, valor, TO_CHAR(data_pagamento, 'DD-MM-YYYY'), status FROM pagamentos WHERE cliente_id=%s AND usuario_id=%s", 
                           (cliente_id, self.usuario_id))
            pagamentos = cursor.fetchall()
            for pagamento in pagamentos:
                self.detalhes_tree.insert("", END, values=pagamento)
            conn.close()

    def editar_cliente(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Por favor, selecione um cliente para editar.")
            return

        cliente_id = self.tree.item(selected_item[0], "values")[0]
        cliente_nome = self.tree.item(selected_item[0], "values")[1]
        cliente_email = self.tree.item(selected_item[0], "values")[2]
        cliente_telefone = self.tree.item(selected_item[0], "values")[3]

        self.editar_cliente_toplevel = Toplevel(self.root)
        self.editar_cliente_toplevel.title("Editar Cliente")

        Label(self.editar_cliente_toplevel, text="Nome", font=("Arial", 12)).grid(row=0, column=0, pady=5, sticky=E)
        Label(self.editar_cliente_toplevel, text="Email", font=("Arial", 12)).grid(row=1, column=0, pady=5, sticky=E)
        Label(self.editar_cliente_toplevel, text="Telefone", font=("Arial", 12)).grid(row=2, column=0, pady=5, sticky=E)

        self.editar_cliente_nome_entry = Entry(self.editar_cliente_toplevel, font=("Arial", 12))
        self.editar_cliente_nome_entry.grid(row=0, column=1, pady=5)
        self.editar_cliente_nome_entry.insert(0, cliente_nome)

        self.editar_cliente_email_entry = Entry(self.editar_cliente_toplevel, font=("Arial", 12))
        self.editar_cliente_email_entry.grid(row=1, column=1, pady=5)
        self.editar_cliente_email_entry.insert(0, cliente_email)

        self.editar_cliente_telefone_entry = Entry(self.editar_cliente_toplevel, font=("Arial", 12))
        self.editar_cliente_telefone_entry.grid(row=2, column=1, pady=5)
        self.editar_cliente_telefone_entry.insert(0, cliente_telefone)

        Button(self.editar_cliente_toplevel, text="Salvar", command=lambda: self.salvar_edicao_cliente(cliente_id), font=("Arial", 12)).grid(row=3, column=0, columnspan=2, pady=10)

    def salvar_edicao_cliente(self, cliente_id):
        nome = self.editar_cliente_nome_entry.get()
        email = self.editar_cliente_email_entry.get()
        telefone = self.editar_cliente_telefone_entry.get()
        editar_cliente(cliente_id, nome, email, telefone, self.usuario_id)
        messagebox.showinfo("Sucesso", "Cliente editado com sucesso!")
        self.editar_cliente_toplevel.destroy()
        self.tree.delete(*self.tree.get_children())  
        self.carregar_clientes_pagamentos()  

    def excluir_cliente(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Por favor, selecione um cliente para excluir.")
            return

        cliente_id = self.tree.item(selected_item[0], "values")[0]
        confirmar = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir este cliente?")
        if confirmar:
            excluir_cliente(cliente_id, self.usuario_id)
            self.show_clientes_pagamentos()  

    def editar_pagamento(self):
        selected_item = self.detalhes_tree.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Por favor, selecione um pagamento para editar.")
            return

        pagamento_id = self.detalhes_tree.item(selected_item[0], "values")[0]
        pagamento_tipo = self.detalhes_tree.item(selected_item[0], "values")[1]
        pagamento_valor = self.detalhes_tree.item(selected_item[0], "values")[2]
        pagamento_data = self.detalhes_tree.item(selected_item[0], "values")[3]
        pagamento_status = self.detalhes_tree.item(selected_item[0], "values")[4]

        self.editar_pagamento_toplevel = Toplevel(self.root)
        self.editar_pagamento_toplevel.title("Editar Pagamento")

        Label(self.editar_pagamento_toplevel, text="Tipo de Pagamento", font=("Arial", 12)).grid(row=0, column=0, pady=5, sticky=E)
        Label(self.editar_pagamento_toplevel, text="Valor", font=("Arial", 12)).grid(row=1, column=0, pady=5, sticky=E)
        Label(self.editar_pagamento_toplevel, text="Data de Pagamento", font=("Arial", 12)).grid(row=2, column=0, pady=5, sticky=E)
        Label(self.editar_pagamento_toplevel, text="Status", font=("Arial", 12)).grid(row=3, column=0, pady=5, sticky=E)

        self.editar_pagamento_tipo_combobox = ttk.Combobox(self.editar_pagamento_toplevel, font=("Arial", 12), values=[
            'PIX', 'Cartão de Débito', 'Cartão de Crédito', 'Dinheiro'
        ])
        self.editar_pagamento_tipo_combobox.grid(row=0, column=1, pady=5)
        self.editar_pagamento_tipo_combobox.set(pagamento_tipo)

        self.editar_pagamento_valor_entry = Entry(self.editar_pagamento_toplevel, font=("Arial", 12))
        self.editar_pagamento_valor_entry.grid(row=1, column=1, pady=5)
        self.editar_pagamento_valor_entry.insert(0, pagamento_valor)
        self.editar_pagamento_valor_entry.bind('<FocusOut>', self.formatar_valor_pagamento)

        self.editar_pagamento_data_entry = Entry(self.editar_pagamento_toplevel, font=("Arial", 12))
        self.editar_pagamento_data_entry.grid(row=2, column=1, pady=5)
        self.editar_pagamento_data_entry.insert(0, pagamento_data)

        self.editar_pagamento_status_combobox = ttk.Combobox(self.editar_pagamento_toplevel, font=("Arial", 12), values=[
            'Pago', 'Em Aberto'
        ])
        self.editar_pagamento_status_combobox.grid(row=3, column=1, pady=5)
        self.editar_pagamento_status_combobox.set(pagamento_status)

        Button(self.editar_pagamento_toplevel, text="Salvar", command=lambda: self.salvar_edicao_pagamento(pagamento_id), font=("Arial", 12)).grid(row=4, column=0, columnspan=2, pady=10)

    def formatar_valor_pagamento(self, event):
        try:
            valor = Decimal(self.editar_pagamento_valor_entry.get().replace('R$', '').replace('.', '').replace(',', '.'))
            self.editar_pagamento_valor_entry.delete(0, END)
            self.editar_pagamento_valor_entry.insert(0, locale.currency(valor, grouping=True))
        except InvalidOperation:
            messagebox.showerror("Erro", "Valor inválido!")

    def salvar_edicao_pagamento(self, pagamento_id):
        tipo_pagamento = self.editar_pagamento_tipo_combobox.get()
        try:
            valor = Decimal(self.editar_pagamento_valor_entry.get().replace('R$', '').replace('.', '').replace(',', '.'))
        except InvalidOperation:
            messagebox.showerror("Erro", "Valor inválido!")
            return
        data_pagamento = self.editar_pagamento_data_entry.get()
        status = self.editar_pagamento_status_combobox.get()
        try:
            editar_pagamento(pagamento_id, tipo_pagamento, valor, data_pagamento, status, self.usuario_id)
            messagebox.showinfo("Sucesso", "Pagamento editado com sucesso!")
            self.editar_pagamento_toplevel.destroy()
            self.mostrar_detalhes_pagamentos(None)  
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao editar o pagamento: {e}")

    def excluir_pagamento(self):
        selected_item = self.detalhes_tree.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Por favor, selecione um pagamento para excluir.")
            return

        pagamento_id = self.detalhes_tree.item(selected_item[0], "values")[0]
        confirmar = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir este pagamento?")
        if confirmar:
            excluir_pagamento(pagamento_id, self.usuario_id)
            self.mostrar_detalhes_pagamentos(None)  

    def show_menu_from_clientes_pagamentos(self):
        self.clientes_pagamentos_frame.pack_forget()
        self.clientes_pagamentos_buttons_frame.pack_forget()
        self.show_menu()

    def show_relatorios(self):
        self.menu_frame.pack_forget()
        if hasattr(self, 'projetos_frame'):
            self.projetos_frame.pack_forget()

        largura_janela = 800
        altura_janela = 600

        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        x_posicao = (largura_tela // 2) - (largura_janela // 2)
        y_posicao = (altura_tela // 2) - (altura_janela // 2)

        self.relatorios_frame = Frame(self.root, width=largura_janela, height=altura_janela)
        self.relatorios_frame.place(x=x_posicao, y=y_posicao)

        Label(self.relatorios_frame, text="Cliente", font=("Arial", 12)).grid(row=0, column=0, sticky=E, pady=5)
        self.relatorios_cliente_id_combobox = ttk.Combobox(self.relatorios_frame, font=("Arial", 12))
        self.relatorios_cliente_id_combobox.grid(row=0, column=1, pady=5)
        self.carregar_clientes_para_relatorio()

        Label(self.relatorios_frame, text="Data Inicial", font=("Arial", 12)).grid(row=1, column=0, sticky=E, pady=5)
        self.relatorios_data_inicial_entry = DateEntry(self.relatorios_frame, font=("Arial", 12), date_pattern='dd-mm-yyyy')
        self.relatorios_data_inicial_entry.grid(row=1, column=1, pady=5)

        Label(self.relatorios_frame, text="Data Final", font=("Arial", 12)).grid(row=2, column=0, sticky=E, pady=5)
        self.relatorios_data_final_entry = DateEntry(self.relatorios_frame, font=("Arial", 12), date_pattern='dd-mm-yyyy')
        self.relatorios_data_final_entry.grid(row=2, column=1, pady=5)

        Label(self.relatorios_frame, text="Tipo de Relatório", font=("Arial", 12)).grid(row=3, column=0, sticky=E, pady=5)
        self.relatorios_tipo_combobox = ttk.Combobox(self.relatorios_frame, font=("Arial", 12), values=[
            'Projetos', 'Pagamentos', 'Ambos'
        ])
        self.relatorios_tipo_combobox.grid(row=3, column=1, pady=5)

        Button(self.relatorios_frame, text="Exportar CSV", command=self.exportar_csv_relatorio, font=("Arial", 12)).grid(row=4, column=0, pady=10)
        Button(self.relatorios_frame, text="Exportar XML", command=self.exportar_xml_relatorio, font=("Arial", 12)).grid(row=4, column=1, pady=10)
        Button(self.relatorios_frame, text="Exportar PDF", command=self.exportar_pdf_relatorio, font=("Arial", 12)).grid(row=4, column=2, pady=10)
        Button(self.relatorios_frame, text="Voltar", command=self.show_menu_from_relatorios, font=("Arial", 12)).grid(row=5, column=0, columnspan=3, pady=10)

    def carregar_clientes_para_relatorio(self):
        conn = conectar_bd()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome FROM clientes WHERE usuario_id=%s", (self.usuario_id,))
            clientes = cursor.fetchall()
            self.relatorios_cliente_id_combobox['values'] = [f"{cliente[0]} - {cliente[1]}" for cliente in clientes]
            conn.close()

    def exportar_csv_relatorio(self):
        cliente_id, tipo_relatorio, data_inicial, data_final = self.obter_parametros_relatorio()
        dados = self.carregar_dados_para_relatorio(cliente_id, tipo_relatorio, data_inicial, data_final)
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filepath:
            exportar_csv(dados, filepath)
            messagebox.showinfo("Sucesso", "Relatório exportado como CSV com sucesso!")

    def exportar_xml_relatorio(self):
        cliente_id, tipo_relatorio, data_inicial, data_final = self.obter_parametros_relatorio()
        dados = self.carregar_dados_para_relatorio(cliente_id, tipo_relatorio, data_inicial, data_final)
        filepath = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")])
        if filepath:
            exportar_xml(dados, filepath)
            messagebox.showinfo("Sucesso", "Relatório exportado como XML com sucesso!")

    def exportar_pdf_relatorio(self):
        cliente_id, tipo_relatorio, data_inicial, data_final = self.obter_parametros_relatorio()
        dados = self.carregar_dados_para_relatorio(cliente_id, tipo_relatorio, data_inicial, data_final)
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if filepath:
            exportar_pdf(dados, filepath)
            messagebox.showinfo("Sucesso", "Relatório exportado como PDF com sucesso!")

    def obter_parametros_relatorio(self):
        cliente_id = int(self.relatorios_cliente_id_combobox.get().split(' - ')[0])
        tipo_relatorio = self.relatorios_tipo_combobox.get()
        data_inicial = self.relatorios_data_inicial_entry.get_date().strftime('%Y-%m-%d')
        data_final = self.relatorios_data_final_entry.get_date().strftime('%Y-%m-%d')
        return cliente_id, tipo_relatorio, data_inicial, data_final

    def carregar_dados_para_relatorio(self, cliente_id, tipo_relatorio, data_inicial, data_final):
        conn = conectar_bd()
        if conn:
            cursor = conn.cursor()
            query = """
                SELECT c.id, c.nome, c.email, c.telefone, p.id, p.tipo_pagamento, p.valor, TO_CHAR(p.data_pagamento, 'DD-MM-YYYY'), p.status 
                FROM clientes c
                LEFT JOIN pagamentos p ON c.id = p.cliente_id
                WHERE c.usuario_id = %s AND c.id = %s
                AND p.data_pagamento BETWEEN %s AND %s
            """
            cursor.execute(query, (self.usuario_id, cliente_id, data_inicial, data_final))
            dados_pagamentos = cursor.fetchall()

            if tipo_relatorio in ['Projetos', 'Ambos']:
                query_projetos = """
                    SELECT c.id, c.nome, c.email, c.telefone, pr.id, pr.tipo_projeto, pr.valor, TO_CHAR(pr.data_entrega, 'DD-MM-YYYY'), pr.recorrente
                    FROM clientes c
                    LEFT JOIN projetos pr ON c.id = pr.cliente_id
                    WHERE c.usuario_id = %s AND c.id = %s
                    AND pr.data_entrega BETWEEN %s AND %s
                """
                cursor.execute(query_projetos, (self.usuario_id, cliente_id, data_inicial, data_final))
                dados_projetos = cursor.fetchall()
            else:
                dados_projetos = []

            conn.close()
            if tipo_relatorio == 'Ambos':
                return dados_pagamentos + dados_projetos
            elif tipo_relatorio == 'Pagamentos':
                return dados_pagamentos
            else:
                return dados_projetos
        return []

    def show_menu_from_relatorios(self):
        self.relatorios_frame.pack_forget()
        self.show_menu()

    def show_cadastrar_projeto(self):
        self.menu_frame.pack_forget()
        if hasattr(self, 'projetos_frame'):
            self.projetos_frame.pack_forget()  

        self.cadastrar_projeto_frame = Frame(self.root)
        self.cadastrar_projeto_frame.place(relx=0.5, rely=0.5, anchor=CENTER)  

        Label(self.cadastrar_projeto_frame, text="Cadastrar Projeto", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=10)

        Label(self.cadastrar_projeto_frame, text="Cliente", font=("Arial", 12)).grid(row=1, column=0, sticky=E, pady=5)
        self.projeto_cliente_id_combobox = ttk.Combobox(self.cadastrar_projeto_frame, font=("Arial", 12))
        self.projeto_cliente_id_combobox.grid(row=1, column=1, pady=5)
        self.carregar_clientes_para_projetos()

        Label(self.cadastrar_projeto_frame, text="Nome do Projeto", font=("Arial", 12)).grid(row=2, column=0, sticky=E, pady=5)
        self.projeto_nome_entry = Entry(self.cadastrar_projeto_frame, font=("Arial", 12))
        self.projeto_nome_entry.grid(row=2, column=1, pady=5)

        Label(self.cadastrar_projeto_frame, text="Tipo de Projeto", font=("Arial", 12)).grid(row=3, column=0, sticky=E, pady=5)
        self.projeto_tipo_combobox = ttk.Combobox(self.cadastrar_projeto_frame, font=("Arial", 12), values=[
            'Website', 'Aplicativo', 'Marketing', 'Consultoria'
        ])
        self.projeto_tipo_combobox.grid(row=3, column=1, pady=5)

        Label(self.cadastrar_projeto_frame, text="Valor (R$)", font=("Arial", 12)).grid(row=4, column=0, sticky=E, pady=5)
        self.projeto_valor_entry = Entry(self.cadastrar_projeto_frame, font=("Arial", 12))
        self.projeto_valor_entry.grid(row=4, column=1, pady=5)
        self.projeto_valor_entry.bind('<FocusOut>', self.formatar_valor_projeto)

        Label(self.cadastrar_projeto_frame, text="Data de Entrega", font=("Arial", 12)).grid(row=5, column=0, sticky=E, pady=5)
        self.projeto_data_entry = Entry(self.cadastrar_projeto_frame, font=("Arial", 12))
        self.projeto_data_entry.grid(row=5, column=1, pady=5)

        Button(self.cadastrar_projeto_frame, text="Selecionar Data", command=self.mostrar_calendario_projeto, font=("Arial", 12)).grid(row=5, column=2, pady=5, padx=5)

        Label(self.cadastrar_projeto_frame, text="Recorrente", font=("Arial", 12)).grid(row=6, column=0, sticky=E, pady=5)
        self.projeto_recorrente_var = BooleanVar()
        Checkbutton(self.cadastrar_projeto_frame, variable=self.projeto_recorrente_var, onvalue=True, offvalue=False).grid(row=6, column=1, pady=5)

        Button(self.cadastrar_projeto_frame, text="Salvar", command=self.salvar_projeto, font=("Arial", 12)).grid(row=7, column=0, columnspan=2, pady=10)
        Button(self.cadastrar_projeto_frame, text="Voltar", command=self.show_menu_from_projeto, font=("Arial", 12)).grid(row=8, column=0, columnspan=2, pady=10)

    def mostrar_calendario_projeto(self):
        self.calendario_toplevel = Toplevel(self.root)
        self.calendario = Calendar(self.calendario_toplevel, date_pattern='dd-mm-yyyy')
        self.calendario.pack()
        Button(self.calendario_toplevel, text="Selecionar", command=self.selecionar_data_projeto).pack()

    def selecionar_data_projeto(self):
        self.projeto_data_entry.delete(0, END)
        self.projeto_data_entry.insert(0, self.calendario.get_date())
        self.calendario_toplevel.destroy()

    def carregar_clientes_para_projetos(self):
        conn = conectar_bd()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome FROM clientes WHERE usuario_id=%s", (self.usuario_id,))
            clientes = cursor.fetchall()
            self.projeto_cliente_id_combobox['values'] = [f"{cliente[0]} - {cliente[1]}" for cliente in clientes]
            conn.close()

    def formatar_valor_projeto(self, event):
        try:
            valor = Decimal(self.projeto_valor_entry.get().replace('R$', '').replace('.', '').replace(',', '.'))
            self.projeto_valor_entry.delete(0, END)
            self.projeto_valor_entry.insert(0, locale.currency(valor, grouping=True))
        except InvalidOperation:
            messagebox.showerror("Erro", "Valor inválido!")

    def salvar_projeto(self):
        cliente_id = int(self.projeto_cliente_id_combobox.get().split(' - ')[0])
        nome_projeto = self.projeto_nome_entry.get()
        tipo_projeto = self.projeto_tipo_combobox.get()
        try:
            valor = Decimal(self.projeto_valor_entry.get().replace('R$', '').replace('.', '').replace(',', '.'))
        except InvalidOperation:
            messagebox.showerror("Erro", "Valor inválido!")
            return
        data_entrega = self.projeto_data_entry.get()
        recorrente = self.projeto_recorrente_var.get()
        cadastrar_projeto(cliente_id, nome_projeto, tipo_projeto, valor, data_entrega, recorrente, self.usuario_id)
        messagebox.showinfo("Sucesso", "Projeto cadastrado com sucesso!")
        self.projeto_cliente_id_combobox.set('')
        self.projeto_nome_entry.delete(0, END)
        self.projeto_tipo_combobox.set('')
        self.projeto_valor_entry.delete(0, END)
        self.projeto_data_entry.delete(0, END)
        self.projeto_recorrente_var.set(False)

    def show_menu_from_projeto(self):
        self.cadastrar_projeto_frame.place_forget()
        self.show_menu()

    def editar_projeto(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Por favor, selecione um projeto para editar.")
            return

        projeto_id = self.tree.item(selected_item[0], "values")[4]
        cliente_nome = self.tree.item(selected_item[0], "values")[0]
        nome_projeto = self.tree.item(selected_item[0], "values")[1]
        data_entrega = self.tree.item(selected_item[0], "values")[2]
        recorrente_texto = self.tree.item(selected_item[0], "values")[3]

        if hasattr(self, 'editar_projeto_toplevel') and self.editar_projeto_toplevel.winfo_exists():
            self.editar_projeto_toplevel.focus()
            return

        self.editar_projeto_toplevel = Toplevel(self.root)
        self.editar_projeto_toplevel.title("Editar Projeto")

        Label(self.editar_projeto_toplevel, text="Cliente", font=("Arial", 12)).grid(row=0, column=0, pady=5, sticky=E)
        Label(self.editar_projeto_toplevel, text="Nome do Projeto", font=("Arial", 12)).grid(row=1, column=0, pady=5, sticky=E)
        Label(self.editar_projeto_toplevel, text="Tipo de Projeto", font=("Arial", 12)).grid(row=2, column=0, pady=5, sticky=E)
        Label(self.editar_projeto_toplevel, text="Valor", font=("Arial", 12)).grid(row=3, column=0, pady=5, sticky=E)
        Label(self.editar_projeto_toplevel, text="Data de Entrega", font=("Arial", 12)).grid(row=4, column=0, pady=5, sticky=E)
        Label(self.editar_projeto_toplevel, text="Recorrente", font=("Arial", 12)).grid(row=5, column=0, pady=5, sticky=E)

        Label(self.editar_projeto_toplevel, text=cliente_nome, font=("Arial", 12, "bold")).grid(row=0, column=1, pady=5, sticky=W)

        self.editar_projeto_nome_entry = Entry(self.editar_projeto_toplevel, font=("Arial", 12))
        self.editar_projeto_nome_entry.grid(row=1, column=1, pady=5)
        self.editar_projeto_nome_entry.insert(0, nome_projeto)

        self.editar_projeto_tipo_combobox = ttk.Combobox(self.editar_projeto_toplevel, font=("Arial", 12), values=[
            'Website', 'Aplicativo', 'Marketing', 'Consultoria'
        ])
        self.editar_projeto_tipo_combobox.grid(row=2, column=1, pady=5)
        self.editar_projeto_tipo_combobox.set('')

        self.editar_projeto_valor_entry = Entry(self.editar_projeto_toplevel, font=("Arial", 12))
        self.editar_projeto_valor_entry.grid(row=3, column=1, pady=5)
        self.editar_projeto_valor_entry.bind('<FocusOut>', self.formatar_valor_edicao_projeto)

        self.editar_projeto_data_entry = Entry(self.editar_projeto_toplevel, font=("Arial", 12))
        self.editar_projeto_data_entry.grid(row=4, column=1, pady=5)
        self.editar_projeto_data_entry.insert(0, data_entrega)

        self.editar_projeto_recorrente_var = BooleanVar()
        Checkbutton(self.editar_projeto_toplevel, variable=self.editar_projeto_recorrente_var, onvalue=True, offvalue=False).grid(row=5, column=1, pady=5)

        if recorrente_texto == "Mensal":
            self.editar_projeto_recorrente_var.set(True)

        Button(self.editar_projeto_toplevel, text="Salvar", command=lambda: self.salvar_edicao_projeto(projeto_id), font=("Arial", 12)).grid(row=6, column=0, columnspan=2, pady=10)

    def formatar_valor_edicao_projeto(self, event):
        try:
            valor = Decimal(self.editar_projeto_valor_entry.get().replace('R$', '').replace('.', '').replace(',', '.'))
            self.editar_projeto_valor_entry.delete(0, END)
            self.editar_projeto_valor_entry.insert(0, locale.currency(valor, grouping=True))
        except InvalidOperation:
            messagebox.showerror("Erro", "Valor inválido!")

    def salvar_edicao_projeto(self, projeto_id):
        nome_projeto = self.editar_projeto_nome_entry.get()
        tipo_projeto = self.editar_projeto_tipo_combobox.get()
        try:
            valor = Decimal(self.editar_projeto_valor_entry.get().replace('R$', '').replace('.', '').replace(',', '.'))
        except InvalidOperation:
            messagebox.showerror("Erro", "Valor inválido!")
            return
        data_entrega = self.editar_projeto_data_entry.get()
        recorrente = self.editar_projeto_recorrente_var.get()
        editar_projeto(projeto_id, nome_projeto, tipo_projeto, valor, data_entrega, recorrente, self.usuario_id)
        messagebox.showinfo("Sucesso", "Projeto editado com sucesso!")
        self.editar_projeto_toplevel.destroy()  
        self.mostrar_projetos_cadastrados()  

    def excluir_projeto(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Por favor, selecione um projeto para excluir.")
            return

        projeto_id = self.tree.item(selected_item[0], "values")[4]
        confirmar = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir este projeto?")
        if confirmar:
            excluir_projeto(projeto_id, self.usuario_id)
            self.mostrar_projetos_cadastrados()  

criar_tabelas()

root = Tk()
app = Application(root)
root.mainloop()