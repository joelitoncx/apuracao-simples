# Automação — Apuração do Simples Nacional

Projeto em Python para automatizar a apuração mensal do Simples Nacional,
desenvolvido para o município de Coxim/MS.

## O que o sistema faz

- Acessa o portal NFS-e e exporta as notas fiscais do período
- Calcula o total das notas autorizadas via XML
- Acessa o portal do Simples Nacional e preenche o PGDAS-D
- Transmite a declaração e gera o DAS automaticamente

## Tecnologias utilizadas

- Python 3.12+
- Selenium (automação web)
- openpyxl (leitura de planilhas)
- Tkinter (interface gráfica)
- webdriver-manager (gerenciamento do ChromeDriver)

## Como usar

### 1. Clone o repositório

git clone https://github.com/SEU_USUARIO/apuracao-simples.git

cd apuracao-simples

### 2. Crie o ambiente virtual

python -m venv venv

venv\Scripts\activate


### 3. Instale as dependências

pip install selenium openpyxl webdriver-manager

### 4. Configure a planilha de credenciais
Renomeie `credenciais_exemplo.xlsx` para `credenciais.xlsx`
e preencha com os dados reais de cada empresa.

### 5. Execute a interface

python interface.py

## Estrutura do projeto

apuracao_simples/

├── main.py                  # Lógica de automação

├── interface.py             # Interface gráfica

├── config.py                # Configurações (URLs, caminhos)

├── credenciais_exemplo.xlsx # Modelo da planilha

└── README.md

## Observações

- O sistema realiza uma pausa para resolução manual do CAPTCHA
- Desenvolvido para uso com Google Chrome
- Testado no Windows 10/11

