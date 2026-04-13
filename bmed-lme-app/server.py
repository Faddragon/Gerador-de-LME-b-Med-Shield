from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='public', static_url_path='')
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-default-123')

@app.route('/')
def index():
    return app.send_static_file('index.html')

# Renderiza o HTML visual em vez de usar biblioteca de PDF
@app.route('/gerar_lme_html', methods=['POST'])
def gerar_lme_html():
    dados_json = request.form.get('dados_json')
    if not dados_json:
        return "Erro: Dados não recebidos", 400
    
    dados = json.loads(dados_json)
    # Envia os dados para preencher o nosso novo template visual
    return render_template('lme_impressao.html', dados=dados)

# NOVA ROTA: (Com o @ e antes do app.run!)
@app.route('/pdfs/<path:filename>')
def serve_pdf(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir_rel = os.getenv('PDF_DATA_DIR', os.path.join('data', 'pcdt 12-4-26'))
    diretorio_pdfs = os.path.join(base_dir, data_dir_rel)
    caminho_completo = os.path.join(diretorio_pdfs, filename)
    
    # --- MÁQUINA DA VERDADE (DEBUG) ---
    print("\n" + "="*40)
    print("🚨 ALARME DE BUSCA DE PDF 🚨")
    print(f"O navegador pediu o arquivo: '{filename}'")
    print(f"O Python está procurando em: '{caminho_completo}'")
    print(f"O Windows diz que o arquivo existe? -> {os.path.exists(caminho_completo)}")
    print("="*40 + "\n")
    
    return send_from_directory(diretorio_pdfs, filename)


# O app.run DEVE ser sempre a última coisa do arquivo!
if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() in ['true', '1', 't']
    app.run(port=port, debug=debug_mode)