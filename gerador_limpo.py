import os
import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime

def gerar_lme_limpo(dados_extraidos):
    base_path = os.path.dirname(os.path.abspath(__file__))
    caminho_template = os.path.join(base_path, "public", "lme limpo.pdf")
    pasta_saida = os.path.join(base_path, "output")

    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)

    # 1. Criar a camada de texto usando coordenadas (X, Y)
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 10)

    # Coordenadas ajustadas para o seu "lme limpo.pdf"
    # O ponto (0,0) é o canto inferior esquerdo da página
    can.drawString(100, 678, dados_extraidos.get('nome', ''))     # Nome Paciente
    can.drawString(100, 653, dados_extraidos.get('mae', ''))      # Nome Mãe
    can.drawString(410, 678, dados_extraidos.get('peso', ''))     # Peso
    can.drawString(500, 678, dados_extraidos.get('altura', ''))   # Altura
    
    # Medicamento e Quantidade
    can.drawString(75, 595, dados_extraidos.get('med', ''))       # Medicamento
    can.drawString(405, 595, "CP")                                # Qtd 1º Mês

    # Diagnóstico e CID
    can.drawString(75, 525, dados_extraidos.get('cid', ''))       # CID-10
    can.drawString(140, 525, dados_extraidos.get('diag', ''))     # Diagnóstico
    
    # Anamnese (Quebra manual simples ou linha única)
    can.drawString(75, 495, dados_extraidos.get('anamnese', '')[:90]) 
    
    # Médico e Data
    can.drawString(100, 315, dados_extraidos.get('medico', ''))   # Nome Médico
    can.drawString(400, 315, dados_extraidos.get('data', ''))     # Data
    can.drawString(100, 290, dados_extraidos.get('cns_med', ''))  # CNS/CPF Médico

    can.save()
    packet.seek(0)

    # 2. Mesclar a camada de texto com o PDF original
    try:
        new_pdf = PdfReader(packet)
        existing_pdf = PdfReader(caminho_template)
        output = PdfWriter()

        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)

        nome_arq = dados_extraidos.get('nome', 'LME').replace(' ', '_')
        caminho_final = os.path.join(pasta_saida, f"LME_{nome_arq}.pdf")

        with open(caminho_final, "wb") as f:
            output.write(f)
        
        return caminho_final
    except Exception as e:
        print(f"Erro ao mesclar PDF: {e}")
        return None