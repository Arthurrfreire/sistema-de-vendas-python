## Sistema de Gerenciamento de Clientes

Este é um aplicativo de gerenciamento de clientes, pagamentos e projetos desenvolvido em Python com interface gráfica usando Tkinter e Tkcalendar, e com persistência de dados em um banco de dados local SQLite. O sistema permite o cadastro e login de usuários, gerenciamento de clientes, pagamentos, e projetos, e geração de relatórios em formatos CSV, XML e PDF.

## Funcionalidades

**Login e Cadastro de Usuários:** Usuários podem se registrar e fazer login no sistema com senhas protegidas por hash usando bcrypt.

**Gerenciamento de Clientes:** Possibilidade de adicionar, editar, excluir e visualizar clientes.

**Gerenciamento de Pagamentos:** Permite cadastrar, editar, excluir e visualizar pagamentos realizados pelos clientes.

**Gerenciamento de Projetos:** Permite cadastrar, editar, excluir e visualizar projetos dos clientes, incluindo projetos recorrentes.

**Alertas de Pagamentos e Projetos:** O sistema alerta o usuário sobre pagamentos e projetos com vencimento ou entrega próxima (7 dias).

**Exportação de Dados:** Relatórios de clientes e pagamentos podem ser exportados nos formatos CSV, XML e PDF.

**Persistência de Dados com SQLite:** Os dados são armazenados em um banco de dados local SQLite (clientes.db), facilitando a portabilidade do sistema.

## Tecnologias Utilizadas

  **Python:** Linguagem de programação.

  **Tkinter:** Para interface gráfica.

  **Tkcalendar:** Para seleção de datas.

  **bcrypt:** Para criptografia de senhas.

  **SQLite:** Banco de dados local.

  **FPDF:** Para gerar relatórios em PDF.

  **CSV e XML.etree.ElementTree:** Para gerar relatórios em CSV e XML.

## Instalação e Configuração

**1. Clone o Repositório**

    git clone https://github.com/seu_usuario/sistema-gerenciamento-clientes.git
    cd sistema-gerenciamento-clientes

**2. Crie um Ambiente Virtual (Opcional)**

Recomenda-se usar um ambiente virtual para isolar as dependências do projeto:

    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate  # Windows
    
**3. Instale as Dependências**

As bibliotecas necessárias estão listadas no arquivo requirements.txt. Instale-as com o seguinte comando:

    pip install -r requirements.txt
    
**4. Execução**

Após configurar o ambiente e instalar as dependências, execute o script principal:

    python sistema_gerenciamento.py
    
**5. Criar Executável (Opcional)**
   
Para gerar um executável que possa ser usado sem a necessidade de instalar Python e bibliotecas, use o PyInstaller:

    pip install pyinstaller
    pyinstaller --onefile sistema_gerenciamento.py
    O executável será gerado na pasta dist/.

## Uso

**Tela de Login:**
![Tela de login](https://i.imgur.com/SkrrUL0.png)

Na primeira execução, você pode se registrar como um novo usuário.
Após registrar, faça login para acessar o sistema.

**Menu Principal:**
![Tela de login](https://i.imgur.com/jJxqLpi.png)

O sistema permite que você cadastre clientes, pagamentos e projetos.
É possível gerar relatórios e exportá-los em formatos CSV, XML ou PDF.

**Alertas:**

O sistema exibe alertas automáticos de pagamentos e projetos com vencimento ou entrega próxima (7 dias).
Estrutura do Banco de Dados (SQLite)

**Usuarios:**

    id (INTEGER PRIMARY KEY): ID do usuário.
    username (TEXT UNIQUE): Nome de usuário.
    password (TEXT): Senha criptografada.

**Clientes:**

    id (INTEGER PRIMARY KEY): ID do cliente.
    nome (TEXT): Nome do cliente.
    email (TEXT): Email do cliente.
    telefone (TEXT): Telefone do cliente.
    usuario_id (INTEGER): ID do usuário (chave estrangeira).

**Pagamentos:**

    id (INTEGER PRIMARY KEY): ID do pagamento.
    cliente_id (INTEGER): ID do cliente (chave estrangeira).
    tipo_pagamento (TEXT): Tipo de pagamento (PIX, Cartão, etc.).
    valor (DECIMAL): Valor do pagamento.
    data_pagamento (DATE): Data do pagamento.
    status (TEXT): Status do pagamento (Pago, Em Aberto).
    usuario_id (INTEGER): ID do usuário (chave estrangeira).

**Projetos:**

    id (INTEGER PRIMARY KEY): ID do projeto.
    cliente_id (INTEGER): ID do cliente (chave estrangeira).
    nome_projeto (TEXT): Nome do projeto.
    tipo_projeto (TEXT): Tipo de projeto (Website, Aplicativo, etc.).
    valor (DECIMAL): Valor do projeto.
    data_entrega (DATE): Data de entrega do projeto.
    recorrente (BOOLEAN): Se o projeto é recorrente.
    usuario_id (INTEGER): ID do usuário (chave estrangeira).

## Dependências

As principais dependências do projeto são:

**Tkinter:** Biblioteca nativa para GUI em Python.

**Tkcalendar:** Para entrada de data.

**bcrypt:** Para hashing de senhas.

**sqlite3:** Para o banco de dados local.

**FPDF:** Para exportar relatórios em PDF.

**csv:** Para exportar dados em CSV.

**xml.etree.ElementTree:** Para exportar dados em XML.


## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
