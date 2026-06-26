import openpyxl
import time
import os
import glob
import zipfile
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config import CAMINHO_PLANILHA, URL_NFSE, URL_SIMPLES

# Variáveis dinâmicas — atualizadas pela interface antes de executar
MES_EXPORTACAO = "6"
ANO_EXPORTACAO = "2026"
MES_ANO        = "06/2026"


def ler_empresas():
    """Lê todas as empresas da planilha e retorna uma lista de dicionários."""
    pasta = openpyxl.load_workbook(CAMINHO_PLANILHA)
    aba   = pasta.active
    empresas = []

    for linha in aba.iter_rows(min_row=2, values_only=True):
        if linha[0]:  # ignora linhas vazias
            empresas.append({
                "NOME_EMPRESA":    str(linha[0]),
                "LOGIN_NFSE":      str(linha[1]),
                "SENHA_NFSE":      str(linha[2]),
                "CNPJ":            str(linha[3]),
                "CPF_RESPONSAVEL": str(linha[4]),
                "CODIGO_ACESSO":   str(linha[5]),
            })
    return empresas


def abrir_navegador():
    servico   = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=servico)
    navegador.maximize_window()
    navegador.get(URL_NFSE)
    return navegador


def fazer_login_nfse(navegador, credenciais):
    wait = WebDriverWait(navegador, 10)
    wait.until(EC.presence_of_element_located((By.ID, "identificador")))
    navegador.find_element(By.ID, "identificador").send_keys(credenciais["LOGIN_NFSE"])
    navegador.find_element(By.ID, "senha").send_keys(credenciais["SENHA_NFSE"])
    navegador.find_element(By.XPATH, "//button[contains(text(), 'Acessar')]").click()


def exportar_notas(navegador):
    wait = WebDriverWait(navegador, 10)
    menu = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//a[@href='/nota-fiscal']")))
    menu.click()
    btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(., 'Exportar Notas')]")))
    btn.click()


def preencher_exportar(navegador):
    wait = WebDriverWait(navegador, 10)
    campo_mes = wait.until(EC.presence_of_element_located((By.ID, "mes")))
    campo_mes.clear()
    campo_mes.send_keys(MES_EXPORTACAO)
    campo_ano = navegador.find_element(By.ID, "ano")
    campo_ano.clear()
    campo_ano.send_keys(ANO_EXPORTACAO)
    btn_exportar = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//form//button[contains(., 'Exportar')]")))
    navegador.execute_script("arguments[0].click();", btn_exportar)


def aguardar_download(timeout=60):
    """Aguarda o ZIP aparecer na pasta Downloads."""
    pasta = os.path.expanduser(r"~\Downloads")
    for _ in range(timeout):
        zips = glob.glob(os.path.join(pasta, "NFSe_XML_*.zip"))
        if zips:
            return True
        time.sleep(5)
    return False


def extrair_total_do_zip():
    pasta_downloads = os.path.expanduser(r"~\Downloads")
    lista_zips      = glob.glob(os.path.join(pasta_downloads, "NFSe_XML_*.zip"))
    zip_mais_recente = max(lista_zips, key=os.path.getctime)

    total     = 0.0
    namespace = {"ns": "http://www.sped.fazenda.gov.br/nfse"}

    with zipfile.ZipFile(zip_mais_recente, "r") as zip_file:
        for nome_arquivo in zip_file.namelist():
            if "AUTORIZADA" in nome_arquivo and nome_arquivo.endswith(".xml"):
                with zip_file.open(nome_arquivo) as arquivo:
                    tree = ET.parse(arquivo)
                    root = tree.getroot()
                    vliq = root.find(".//ns:valores/ns:vLiq", namespace)
                    if vliq is not None:
                        total += float(vliq.text)

    print(f"Valor total das notas autorizadas: R$ {total:.2f}")
    return total


def acessar_simples_nacional(navegador, credenciais):
    wait = WebDriverWait(navegador, 10)
    navegador.get(URL_SIMPLES)
    campo_cnpj = wait.until(EC.presence_of_element_located(
        (By.ID, "ctl00_ContentPlaceHolder_authForm_txtCNPJ")))
    campo_cnpj.send_keys(credenciais["CNPJ"])
    campo_cpf = wait.until(EC.presence_of_element_located(
        (By.ID, "ctl00_ContentPlaceHolder_authForm_txtCPFResponsavel")))
    campo_cpf.send_keys(credenciais["CPF_RESPONSAVEL"])
    campo_codigo = wait.until(EC.presence_of_element_located(
        (By.ID, "ctl00_ContentPlaceHolder_authForm_txtCodigoAcesso")))
    campo_codigo.send_keys(credenciais["CODIGO_ACESSO"])
    btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//input[@value='Continuar']")))
    btn.click()


def acessar_pgdas(navegador):
    wait = WebDriverWait(navegador, 10)
    calculo = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[@class='header' and @aria-controls='grupo_5']")))
    navegador.execute_script("arguments[0].click();", calculo)
    pgdas = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//*[contains(text(), 'PGDAS-D e DEFIS')]")))
    navegador.execute_script("arguments[0].click();", pgdas)


def acessar_declaracao_mensal(navegador):
    wait = WebDriverWait(navegador, 10)
    declaracao = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//a[@href='#collapseOne']")))
    navegador.execute_script("arguments[0].click();", declaracao)
    declarar = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//*[contains(text(), 'Declarar/Retificar')]")))
    navegador.execute_script("arguments[0].click();", declarar)


def preencher_periodo_apuracao(navegador):
    wait = WebDriverWait(navegador, 10)
    campo_pa = wait.until(EC.presence_of_element_located((By.ID, "pa")))
    campo_pa.send_keys(MES_ANO)
    btn_salvar = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[@type='submit']")))
    btn_salvar.click()


def preencher_receita_bruta(navegador, total):
    wait = WebDriverWait(navegador, 10)
    campo_interno = wait.until(EC.presence_of_element_located(
        (By.NAME, "rpaCompInt")))
    campo_interno.clear()
    campo_interno.send_keys(str(total))
    campo_externo = navegador.find_element(By.NAME, "rpaCompExt")
    campo_externo.clear()
    campo_externo.send_keys("0")
    btn_salvar = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[@type='submit' and contains(@class,'btn-success')]")))
    btn_salvar.click()


def selecionar_segregacao(navegador, cnpj):
    """Seleciona a categoria de tributação e salva."""
    wait = WebDriverWait(navegador, 10)
    prestacao = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//a[@data-grupo='7']")))
    navegador.execute_script("arguments[0].click();", prestacao)

    # Monta o data-atividade dinamicamente com o CNPJ da empresa
    cnpj_limpo   = cnpj.replace(".", "").replace("/", "").replace("-", "")
    data_atividade = f"{cnpj_limpo}-14"
    nao_fator_r  = wait.until(EC.element_to_be_clickable(
        (By.XPATH, f"//a[@data-atividade='{data_atividade}']")))
    navegador.execute_script("arguments[0].click();", nao_fator_r)

    btn_salvar = wait.until(EC.presence_of_element_located(
        (By.ID, "btn-salvar")))
    navegador.execute_script("arguments[0].click();", btn_salvar)


def preencher_valor_segregacao(navegador, total):
    """Preenche o valor da receita na linha de segregação e clica em Calcular."""
    wait = WebDriverWait(navegador, 10)

    # Campo de receita na tabela de segregação
    campo_receita = wait.until(EC.presence_of_element_located(
        (By.CLASS_NAME, "receita-valor")))
    campo_receita.clear()

    # Formata o valor no padrão brasileiro: 8093.69 → "8093,69"
    valor_formatado = f"{total:.2f}".replace(".", ",")
    campo_receita.send_keys(valor_formatado)

    # Clica em Calcular
    btn_calcular = wait.until(EC.element_to_be_clickable(
        (By.CLASS_NAME, "btn-calcular")))
    navegador.execute_script("arguments[0].click();", btn_calcular)


def transmitir_declaracao(navegador):
    """Clica em Transmitir após o cálculo."""
    wait = WebDriverWait(navegador, 15)
    btn_transmitir = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(., 'Transmitir')]")))
    navegador.execute_script("arguments[0].click();", btn_transmitir)


def gerar_das(navegador):
    """Clica em Gerar DAS após a transmissão."""
    wait = WebDriverWait(navegador, 15)
    btn_das = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//a[contains(., 'Gerar DAS')]")
    ))
    navegador.execute_script("arguments[0].click();", btn_das)



if __name__ == "__main__":
    empresas = ler_empresas()
    dados    = empresas[0]  # primeira empresa para teste
    print(dados)
    navegador = abrir_navegador()
    fazer_login_nfse(navegador, dados)
    exportar_notas(navegador)
    preencher_exportar(navegador)
    time.sleep(30)
    total = extrair_total_do_zip()
    print(f"Total: R$ {total:.2f}")
    acessar_simples_nacional(navegador, dados)
    input("Resolva o CAPTCHA e pressione Enter para continuar...")
    acessar_pgdas(navegador)
    acessar_declaracao_mensal(navegador)
    preencher_periodo_apuracao(navegador)
    preencher_receita_bruta(navegador, total)
    selecionar_segregacao(navegador, dados["CNPJ"])
    preencher_valor_segregacao(navegador, total)
    transmitir_declaracao(navegador)
    gerar_das(navegador)
    print("✅ DAS gerado! Navegador mantido aberto.")
    input("Pressione Enter para encerrar...")