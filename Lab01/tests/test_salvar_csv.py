import csv

from src.snapshot_projeto import CAMPOS_CSV, salvar_csv


def test_salvar_csv__escreve_cabecalho_e_linhas_corretamente(tmp_path):
    """O CSV gerado deve conter o cabeçalho esperado e os valores exatos das linhas passadas."""
    linha = {
        "numero_issue": 1,
        "titulo": "Teste",
        "status": "Aberto",
        "responsaveis": "alice",
        "url": "http://x",
    }
    caminho = tmp_path / "saida.csv"

    salvar_csv([linha], caminho)

    with caminho.open(newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        assert leitor.fieldnames == CAMPOS_CSV, "O cabeçalho do CSV deve corresponder exatamente a CAMPOS_CSV"
        linhas_lidas = list(leitor)

    assert len(linhas_lidas) == 1, "O CSV deve conter exatamente uma linha de dados"
    assert linhas_lidas[0]["numero_issue"] == "1", "O valor de numero_issue deve corresponder ao informado (como string, formato CSV)"
    assert linhas_lidas[0]["titulo"] == "Teste", "O valor de titulo deve corresponder ao informado"
    assert linhas_lidas[0]["status"] == "Aberto", "O valor de status deve corresponder ao informado"
    assert linhas_lidas[0]["responsaveis"] == "alice", "O valor de responsaveis deve corresponder ao informado"
    assert linhas_lidas[0]["url"] == "http://x", "O valor de url deve corresponder ao informado"


def test_salvar_csv__cria_diretorios_pai_automaticamente(tmp_path):
    """salvar_csv deve criar as pastas intermediárias inexistentes do caminho informado."""
    linha = {
        "numero_issue": 7,
        "titulo": "Outro teste",
        "status": "Em andamento",
        "responsaveis": "bob",
        "url": "http://y",
    }
    caminho = tmp_path / "subpasta" / "aninhada" / "saida.csv"

    salvar_csv([linha], caminho)

    assert caminho.exists(), "O arquivo deve ser criado mesmo que as pastas pai ainda não existissem"
    with caminho.open(newline="", encoding="utf-8") as arquivo:
        linhas_lidas = list(csv.DictReader(arquivo))
    assert len(linhas_lidas) == 1, "O CSV criado em pastas aninhadas deve conter a linha esperada"


def test_salvar_csv__lista_vazia_gera_arquivo_apenas_com_cabecalho(tmp_path):
    """Com uma lista vazia de linhas, o CSV deve ser criado contendo apenas o cabeçalho, sem exceções."""
    caminho = tmp_path / "vazio.csv"

    salvar_csv([], caminho)

    assert caminho.exists(), "O arquivo deve ser criado mesmo quando não há linhas para escrever"
    with caminho.open(newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        assert leitor.fieldnames == CAMPOS_CSV, "O cabeçalho deve ser escrito mesmo sem linhas de dados"
        linhas_lidas = list(leitor)
    assert linhas_lidas == [], "Não deve haver linhas de dados quando a lista de entrada é vazia"
