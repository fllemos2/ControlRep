#!/usr/bin/env python3
"""
Script de testes automatizados
Executa validações do sistema Cattle Control
"""
import os
import sys
import subprocess
import requests
import time
from pathlib import Path

def run_command(cmd, description, cwd=None):
    """Executa comando e retorna resultado"""
    print(f"\n🧪 {description}")
    print(f"   Comando: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        print("   ✅ Sucesso"        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Erro: {e}")
        print(f"   Output: {e.stderr}")
        return False, e.stderr

def test_api_health():
    """Testa se API está respondendo"""
    print("\n🌐 Testando API Health Check")
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ API saudável")
            return True
        else:
            print(f"   ❌ Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
        return False

def test_database_connection():
    """Testa conexão com banco de dados"""
    print("\n🗄️ Testando conexão com banco")
    success, output = run_command(
        "cd backend && poetry run python -c \"from app.db.session import SessionLocal; db = SessionLocal(); db.close(); print('Conexão OK')\"",
        "Testando conexão DB",
        cwd="backend"
    )
    return success

def test_models_import():
    """Testa se todos os modelos podem ser importados"""
    print("\n📦 Testando imports dos modelos")
    models = [
        "app.models.matriz",
        "app.models.cria",
        "app.models.reprodutor",
        "app.models.comprador",
        "app.models.desempenho"
    ]

    for model in models:
        success, output = run_command(
            f"cd backend && poetry run python -c \"import {model}; print('{model} importado')\"",
            f"Importando {model}",
            cwd="backend"
        )
        if not success:
            return False
    return True

def test_schemas_validation():
    """Testa validação dos schemas Pydantic"""
    print("\n📋 Testando schemas Pydantic")
    schemas = [
        "app.schemas.matriz",
        "app.schemas.cria",
        "app.schemas.reprodutor",
        "app.schemas.comprador",
        "app.schemas.desempenho"
    ]

    for schema in schemas:
        success, output = run_command(
            f"cd backend && poetry run python -c \"import {schema}; print('{schema} validado')\"",
            f"Validando {schema}",
            cwd="backend"
        )
        if not success:
            return False
    return True

def test_dependencies():
    """Testa se todas as dependências estão instaladas"""
    print("\n📦 Verificando dependências")
    deps = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "openpyxl",
        "python-multipart"
    ]

    for dep in deps:
        success, output = run_command(
            f"cd backend && poetry run python -c \"import {dep}; print('{dep} disponível')\"",
            f"Verificando {dep}",
            cwd="backend"
        )
        if not success:
            return False
    return True

def run_unit_tests():
    """Executa testes unitários (se existirem)"""
    print("\n🧪 Executando testes unitários")
    if Path("backend/tests").exists():
        success, output = run_command(
            "cd backend && poetry run python -m pytest tests/ -v",
            "Executando pytest",
            cwd="backend"
        )
        return success
    else:
        print("   ⚠️ Nenhum teste encontrado (pasta tests/ não existe)")
        return True

def main():
    """Executa todos os testes"""
    print("🧪 CATTLE CONTROL - SUITE DE TESTES")
    print("=" * 50)

    # Verificar se estamos no diretório correto
    if not Path("backend/pyproject.toml").exists():
        print("❌ Execute este script da raiz do projeto (cattle-control/)")
        sys.exit(1)

    results = []

    # 1. Testar dependências
    results.append(("Dependências", test_dependencies()))

    # 2. Testar imports dos modelos
    results.append(("Models Import", test_models_import()))

    # 3. Testar schemas
    results.append(("Schemas Pydantic", test_schemas_validation()))

    # 4. Testar conexão DB
    results.append(("Database Connection", test_database_connection()))

    # 5. Iniciar API para testes
    print("\n🚀 Iniciando API para testes...")
    api_process = None
    try:
        api_process = subprocess.Popen(
            ["cd", "backend", "&&", "poetry", "run", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        time.sleep(3)  # Aguardar inicialização

        # 6. Testar API
        results.append(("API Health Check", test_api_health()))

        # 7. Testar endpoints básicos
        print("\n🔗 Testando endpoints básicos")
        try:
            response = requests.get("http://127.0.0.1:8000/", timeout=5)
            results.append(("API Root Endpoint", response.status_code == 200))
        except:
            results.append(("API Root Endpoint", False))

        # 8. Testar documentação
        try:
            response = requests.get("http://127.0.0.1:8000/docs", timeout=5)
            results.append(("API Documentation", response.status_code == 200))
        except:
            results.append(("API Documentation", False))

    except Exception as e:
        print(f"   ❌ Erro ao iniciar API: {e}")
        results.append(("API Tests", False))
    finally:
        if api_process:
            api_process.terminate()
            api_process.wait()

    # 9. Executar testes unitários
    results.append(("Unit Tests", run_unit_tests()))

    # Resultado final
    print("\n" + "=" * 50)
    print("📊 RESULTADO DOS TESTES")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print("25")
        if success:
            passed += 1

    print(f"\n🎯 SCORE: {passed}/{total} testes passaram")

    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        return 0
    else:
        print("⚠️ ALGUNS TESTES FALHARAM - VERIFIQUE OS ERROS ACIMA")
        return 1

if __name__ == "__main__":
    sys.exit(main())
