#!/usr/bin/env python3
"""
Script de inicialização do desenvolvimento
Executa setup completo do ambiente de desenvolvimento
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Executa comando e mostra resultado"""
    print(f"\n🔧 {description}")
    print(f"   Comando: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("   ✅ Sucesso"        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Erro: {e}")
        print(f"   Output: {e.output}")
        return False

def main():
    """Setup completo do ambiente"""
    print("🚀 CATTLE CONTROL - SETUP DESENVOLVIMENTO")
    print("=" * 50)

    # Verificar se estamos no diretório correto
    if not Path("backend/pyproject.toml").exists():
        print("❌ Execute este script da raiz do projeto (cattle-control/)")
        sys.exit(1)

    # 1. Setup Poetry
    if not run_command("poetry --version", "Verificando Poetry"):
        print("📦 Instalando Poetry...")
        run_command("curl -sSL https://install.python-poetry.org | python3 -", "Instalando Poetry")

    # 2. Instalar dependências
    if not run_command("cd backend && poetry install", "Instalando dependências Python"):
        sys.exit(1)

    # 3. Verificar Python
    if not run_command("cd backend && poetry run python --version", "Verificando Python"):
        sys.exit(1)

    # 4. Criar .env se não existir
    env_file = Path("backend/.env")
    if not env_file.exists():
        print("\n📝 Criando arquivo .env...")
        env_content = """# Database
DATABASE_URL=sqlite:///./cattle_control.db

# API
API_V1_STR=/api/v1
PROJECT_NAME=Cattle Control API
PROJECT_VERSION=0.1.0

# Security
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Debug
DEBUG=True

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080", "http://localhost:5173"]
"""
        env_file.write_text(env_content)
        print("   ✅ Arquivo .env criado")

    # 5. Inicializar banco de dados
    print("\n🗄️ Inicializando banco de dados...")
    if run_command("cd backend && poetry run python -c \"from app.db.session import engine; from app.db.base import Base; Base.metadata.create_all(bind=engine); print('Banco criado com sucesso')\"", "Criando tabelas"):
        print("   ✅ Tabelas criadas")

    # 6. Verificar se API inicia
    print("\n🌐 Testando API...")
    # Iniciar em background por 5 segundos
    import time
    try:
        proc = subprocess.Popen(
            ["cd", "backend", "&&", "poetry", "run", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3)  # Aguardar inicialização

        # Testar health check
        import requests
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=2)
            if response.status_code == 200:
                print("   ✅ API funcionando (health check OK)")
            else:
                print(f"   ⚠️ API iniciou mas health check falhou: {response.status_code}")
        except:
            print("   ⚠️ API iniciou mas não conseguiu testar health check")

        proc.terminate()
        proc.wait()

    except Exception as e:
        print(f"   ❌ Erro ao testar API: {e}")

    print("\n" + "=" * 50)
    print("🎉 SETUP CONCLUÍDO!")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("   1. poetry shell  # Ativar ambiente virtual")
    print("   2. cd backend")
    print("   3. poetry run uvicorn app.main:app --reload  # Iniciar API")
    print("   4. Abrir http://localhost:8000/docs  # Documentação API")
    print("\n📁 ESTRUTURA PRONTA:")
    print("   - Backend FastAPI configurado")
    print("   - Banco SQLite criado")
    print("   - Dependências instaladas")
    print("   - Ambiente virtual pronto")

if __name__ == "__main__":
    main()
