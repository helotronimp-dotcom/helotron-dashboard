import requests
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from zoneinfo import ZoneInfo

PRODUTOS = [
    {"interno": "Cortador de Alimentos 16 em 1",     "busca": "cortador fatiador legumes 16 em 1"},
    {"interno": "Fatiador Rotativo de Legumes",       "busca": "ralador fatiador legumes manual inox"},
    {"interno": "Kit 7 Potes Hermeticos",             "busca": "kit 7 potes hermeticos acrilico"},
    {"interno": "Conjunto Potes Organizadores",       "busca": "organizador geladeira pote hermetico 3 pecas"},
    {"interno": "Tapete de Silicone para Cozinha",    "busca": "descanso panela silicone antitermico"},
    {"interno": "Spray de Oleo Cozinha",              "busca": "pulverizador spray oleo cozinha vidro"},
    {"interno": "Luminaria Solar Flamingo 2 un.",     "busca": "luminaria solar flamingo jardim 2"},
    {"interno": "Luminaria Solar Flamingo 3 un.",     "busca": "enfeite solar flamingo jardim 3"},
    {"interno": "Luminaria Solar Hortensia 3 Hastes", "busca": "luminaria solar hortensia jardim 3 hastes"},
    {"interno": "Luminaria Solar Hortensia PVC",      "busca": "luz solar hortensia pvc jardim"},
    {"interno": "Luminaria Solar Hortensia Ferro",    "busca": "luz solar hortensia ferro jardim"},
]

NOSSOS_PRECOS = {
    "Cortador de Alimentos 16 em 1":     None,
    "Fatiador Rotativo de Legumes":      None,
    "Kit 7 Potes Hermeticos":            110.00,
    "Conjunto Potes Organizadores":      None,
    "Tapete de Silicone para Cozinha":   44.90,
    "Spray de Oleo Cozinha":             None,
    "Luminaria Solar Flamingo 2 un.":    None,
    "Luminaria Solar Flamingo 3 un.":    None,
    "Luminaria Solar Hortensia 3 Hastes": 89.90,
    "Luminaria Solar Hortensia PVC":     None,
    "Luminaria Solar Hortensia Ferro":   None,
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.mercadolivre.com.br/",
    "Origin": "https://www.mercadolivre.com.br",
}

def buscar_precos_ml(busca):
    import time, random
    url = "https://api.mercadolibre.com/sites/MLB/search"
    params = {"q": busca, "limit": 50}
    try:
        time.sleep(random.uniform(2, 4))
        r = requests.get(url, params=params, headers=HEADERS, timeout=20)
        print(f"  Status HTTP: {r.status_code}")
        if r.status_code != 200:
            print(f"  Resposta: {r.text[:300]}")
            return []
        data = r.json()
        total = data.get("paging", {}).get("total", 0)
        print(f"  Total ML: {total} anúncios encontrados")
        precos = [item["price"] for item in data.get("results", []) if item.get("price", 0) > 5]
        return precos
    except Exception as e:
        print(f"  ERRO ao buscar '{busca}': {e}")
        return []

def analisar(precos):
    if not precos:
        return None
    return {
        "minimo": min(precos),
        "maximo": max(precos),
        "media":  round(sum(precos) / len(precos), 2),
        "total":  len(precos),
    }

def brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def gerar_html(resultados, agora):
    linhas = ""
    for r in resultados:
        nosso = NOSSOS_PRECOS.get(r["produto"])
        nosso_txt = brl(nosso) if nosso else "—"

        if nosso and r["media"]:
            diff = nosso - r["media"]
            if diff < -10:
                status = "🟢 Abaixo do mercado"
            elif diff < 5:
                status = "🟡 Na média"
            else:
                status = "🔴 Acima do mercado"
        else:
            status = "—"

        cor_linha = "#f9f9f9" if resultados.index(r) % 2 == 0 else "#ffffff"
        linhas += f"""
        <tr style="background:{cor_linha}">
            <td style="padding:8px 12px;font-size:13px">{r["produto"]}</td>
            <td style="padding:8px 12px;text-align:center">{brl(r["minimo"]) if r["minimo"] else "—"}</td>
            <td style="padding:8px 12px;text-align:center;font-weight:bold">{brl(r["media"]) if r["media"] else "—"}</td>
            <td style="padding:8px 12px;text-align:center">{brl(r["maximo"]) if r["maximo"] else "—"}</td>
            <td style="padding:8px 12px;text-align:center">{r["anuncios"]}</td>
            <td style="padding:8px 12px;text-align:center">{nosso_txt}</td>
            <td style="padding:8px 12px;text-align:center">{status}</td>
        </tr>"""

    return f"""
    <html><body style="font-family:Arial,sans-serif;background:#f0f0f0;padding:20px">
    <div style="max-width:900px;margin:auto;background:white;border-radius:10px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.1)">
        <div style="background:#2d6a4f;padding:25px;text-align:center">
            <h1 style="color:white;margin:0;font-size:22px">📊 Monitor de Preços — Mercado Livre</h1>
            <p style="color:#b7e4c7;margin:8px 0 0">HELOTRON | Atualizado em: {agora}</p>
        </div>
        <div style="padding:20px">
            <table width="100%" cellspacing="0" style="border-collapse:collapse;border-radius:8px;overflow:hidden">
                <thead>
                    <tr style="background:#2d6a4f;color:white">
                        <th style="padding:10px 12px;text-align:left">Produto</th>
                        <th style="padding:10px 12px">Mínimo</th>
                        <th style="padding:10px 12px">Médio</th>
                        <th style="padding:10px 12px">Máximo</th>
                        <th style="padding:10px 12px">Anúncios</th>
                        <th style="padding:10px 12px">Nosso Preço</th>
                        <th style="padding:10px 12px">Status</th>
                    </tr>
                </thead>
                <tbody>{linhas}</tbody>
            </table>
            <p style="color:#888;font-size:11px;margin-top:20px;text-align:center">
                Dados coletados via API oficial do Mercado Livre • Próxima atualização em 2 dias
            </p>
        </div>
    </div>
    </body></html>"""

def enviar_email(html, agora):
    remetente = os.environ["GMAIL_USER"]
    senha     = os.environ["GMAIL_APP_PASSWORD"]
    destinatario = remetente  # envia para o próprio Gmail da Helotron

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📊 Monitor de Preços ML — {agora}"
    msg["From"]    = remetente
    msg["To"]      = destinatario
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(remetente, senha)
        s.sendmail(remetente, destinatario, msg.as_string())
    print(f"Email enviado para {destinatario}")

def main():
    agora = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M")
    print(f"Iniciando monitoramento — {agora}")

    resultados = []
    erros = 0
    for p in PRODUTOS:
        print(f"Buscando: {p['interno']}...")
        precos = buscar_precos_ml(p["busca"])
        dados  = analisar(precos)
        if not dados:
            erros += 1
        resultados.append({
            "produto": p["interno"],
            "minimo":  dados["minimo"] if dados else None,
            "media":   dados["media"]  if dados else None,
            "maximo":  dados["maximo"] if dados else None,
            "anuncios": dados["total"] if dados else 0,
        })

    # Se todos os produtos vieram sem dados, é falha na coleta — avisa no email
    if erros == len(PRODUTOS):
        print("⚠️ ATENÇÃO: Todos os produtos retornaram sem dados — possível bloqueio da API do ML.")
        html = f"""
        <html><body style="font-family:Arial,sans-serif;background:#f0f0f0;padding:20px">
        <div style="max-width:700px;margin:auto;background:white;border-radius:10px;overflow:hidden">
            <div style="background:#c62828;padding:20px;text-align:center">
                <h1 style="color:white;margin:0;font-size:20px">⚠️ Falha na Coleta de Preços</h1>
                <p style="color:#ffcdd2;margin:6px 0 0">Monitor de Preços ML — {agora}</p>
            </div>
            <div style="padding:20px;font-size:13px;color:#333;">
                <p>A coleta de hoje retornou <strong>zero resultados</strong> para todos os {len(PRODUTOS)} produtos monitorados.</p>
                <p><strong>Causa provável:</strong> A API pública do Mercado Livre está bloqueando requisições originadas dos servidores do GitHub Actions (AWS). Isso acontece quando o ML detecta tráfego automatizado de IPs de nuvem.</p>
                <p><strong>Os dados do monitor local</strong> (monitor_precos.py via Selenium) continuam funcionando normalmente — verifique os CSVs em <code>vendas/dados/</code>.</p>
                <p><strong>Próximo passo:</strong> Avaliar migração do monitor cloud para coleta via Selenium em ambiente próprio, ou autenticação OAuth com a API do ML.</p>
            </div>
        </div>
        </body></html>"""
        enviar_email(html, agora)
        print("Email de erro enviado.")
        return

    html = gerar_html(resultados, agora)
    enviar_email(html, agora)
    print("Concluído!")

if __name__ == "__main__":
    main()
