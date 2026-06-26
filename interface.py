import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import main as automacao


def carregar_empresas():
    """Carrega a lista de empresas da planilha para popular o ComboBox."""
    try:
        empresas = automacao.ler_empresas()
        return empresas
    except Exception as e:
        return []


def executar_automacao(log, empresa, mes, ano):
    try:
        # Atualiza variáveis dinâmicas
        automacao.MES_EXPORTACAO = str(mes)
        automacao.ANO_EXPORTACAO = str(ano)
        automacao.MES_ANO        = f"{mes:02d}/{ano}"

        log(f"🏢 Empresa selecionada: {empresa['NOME_EMPRESA']}")
        log(f"📅 Período: {automacao.MES_ANO}")

        log("🌐 Abrindo navegador...")
        navegador = automacao.abrir_navegador()

        log("🔐 Fazendo login na NFS-e...")
        automacao.fazer_login_nfse(navegador, empresa)

        log("📦 Exportando notas fiscais...")
        automacao.exportar_notas(navegador)
        automacao.preencher_exportar(navegador)

        log("⏳ Aguardando download do ZIP...")
        automacao.aguardar_download()

        log("💰 Calculando valor total das notas...")
        total = automacao.extrair_total_do_zip()
        log(f"✅ Total encontrado: R$ {total:.2f}")

        log("🏛️ Acessando Simples Nacional...")
        automacao.acessar_simples_nacional(navegador, empresa)

        log("⚠️  Resolva o CAPTCHA no navegador e clique em OK aqui...")
        aguardar_captcha()

        log("📊 Acessando PGDAS-D...")
        automacao.acessar_pgdas(navegador)
        automacao.acessar_declaracao_mensal(navegador)
        automacao.preencher_periodo_apuracao(navegador)

        log("📝 Preenchendo receita bruta...")
        automacao.preencher_receita_bruta(navegador, total)

        log("🔖 Selecionando segregação de receita...")
        automacao.selecionar_segregacao(navegador, empresa["CNPJ"])

        log("🔢 Preenchendo valor e calculando...")
        automacao.preencher_valor_segregacao(navegador, total)

        log("📤 Transmitindo declaração...")
        automacao.transmitir_declaracao(navegador)

        log("🧾 Gerando DAS...")
        automacao.gerar_das(navegador)

        log("✅ Processo concluído com sucesso!")

    except Exception as e:
        log(f"❌ Erro: {str(e)}")


def aguardar_captcha():
    janela_captcha = tk.Toplevel()
    janela_captcha.title("CAPTCHA")
    janela_captcha.geometry("300x120")
    janela_captcha.grab_set()
    tk.Label(janela_captcha,
             text="Resolva o CAPTCHA no navegador\ne clique em OK para continuar.",
             pady=20).pack()
    tk.Button(janela_captcha, text="OK — Já resolvi!",
              command=janela_captcha.destroy,
              bg="#4CAF50", fg="white", padx=10).pack()
    janela_captcha.wait_window()


def iniciar():
    # Verifica se uma empresa foi selecionada
    idx = combo_empresa.current()
    if idx < 0:
        tk.messagebox.showwarning("Atenção", "Selecione uma empresa!")
        return

    empresa = empresas[idx]
    mes     = combo_mes.current() + 1
    ano     = int(combo_ano.get())

    btn_iniciar.config(state="disabled", text="Executando...")
    area_log.config(state="normal")
    area_log.delete(1.0, tk.END)

    def log(mensagem):
        area_log.config(state="normal")
        area_log.insert(tk.END, mensagem + "\n")
        area_log.see(tk.END)
        area_log.config(state="disabled")

    def rodar():
        executar_automacao(log, empresa, mes, ano)
        btn_iniciar.config(state="normal", text="▶ Calcular Simples Nacional")

    threading.Thread(target=rodar, daemon=True).start()


# ── Interface ──────────────────────────────────────────────────────────────────
janela = tk.Tk()
janela.title("Apuração Simples Nacional")
janela.geometry("520x520")
janela.resizable(False, False)
janela.configure(bg="#f0f0f0")

from tkinter import messagebox

# Título
tk.Label(janela, text="Apuração Simples Nacional",
         font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=15)

# ── Seleção de empresa ─────────────────────────────────────────────────────────
frame_empresa = tk.Frame(janela, bg="#f0f0f0")
frame_empresa.pack(pady=5, padx=20, fill="x")

tk.Label(frame_empresa, text="Empresa:",
         font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=0, column=0, sticky="w")

empresas = carregar_empresas()
nomes    = [e["NOME_EMPRESA"] for e in empresas]

combo_empresa = ttk.Combobox(frame_empresa, values=nomes,
                              width=45, state="readonly")
if nomes:
    combo_empresa.current(0)
combo_empresa.grid(row=0, column=1, padx=10)

# ── Seleção de período ─────────────────────────────────────────────────────────
frame_periodo = tk.Frame(janela, bg="#f0f0f0")
frame_periodo.pack(pady=10)

tk.Label(frame_periodo, text="Período de Apuração:",
         font=("Arial", 10, "bold"), bg="#f0f0f0").grid(
         row=0, column=0, columnspan=4, pady=5)

tk.Label(frame_periodo, text="Mês:", bg="#f0f0f0").grid(row=1, column=0, padx=10)

meses = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
         "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
combo_mes = ttk.Combobox(frame_periodo, values=meses, width=12, state="readonly")
combo_mes.current(5)
combo_mes.grid(row=1, column=1, padx=10)

tk.Label(frame_periodo, text="Ano:", bg="#f0f0f0").grid(row=1, column=2, padx=10)

anos = [str(a) for a in range(2024, 2031)]
combo_ano = ttk.Combobox(frame_periodo, values=anos, width=8, state="readonly")
combo_ano.set("2026")
combo_ano.grid(row=1, column=3, padx=10)

# ── Botão principal ────────────────────────────────────────────────────────────
btn_iniciar = tk.Button(janela,
                        text="▶ Calcular Simples Nacional",
                        command=iniciar,
                        bg="#4CAF50", fg="white",
                        font=("Arial", 12, "bold"),
                        padx=20, pady=10,
                        relief="flat", cursor="hand2")
btn_iniciar.pack(pady=15)

# ── Área de log ────────────────────────────────────────────────────────────────
tk.Label(janela, text="Progresso:", bg="#f0f0f0",
         font=("Arial", 10)).pack(anchor="w", padx=20)

area_log = scrolledtext.ScrolledText(janela, height=12, width=60,
                                     state="disabled", font=("Courier", 9))
area_log.pack(padx=20, pady=5)

janela.mainloop()