"""
Testes AAA da sugestao de frota (RF03 / RN03 — minimizar ociosidade).
Executar na raiz do projeto: python -m unittest discover tests
"""
import os
import sys
import itertools
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import combinacao_otima  # noqa: E402

# Frota padrao do seed: 2 onibus, 1 micro, 1 van
FROTA_SEED = [("ONIBUS", 44, 2), ("MICRO", 28, 1), ("VAN", 15, 1)]


def assentos(sugestao, frota):
    cap = {tipo: c for tipo, c, _ in frota}
    return sum(item["qtd"] * cap[item["tipo"]] for item in sugestao)


class TestCombinacaoOtima(unittest.TestCase):

    def test_sem_passageiros_nao_sugere_veiculo(self):
        # Arrange
        total = 0
        # Act
        sugestao = combinacao_otima(total, FROTA_SEED)
        # Assert
        self.assertEqual(sugestao, [])

    def test_poucos_passageiros_usa_menor_veiculo(self):
        # Arrange — bug antigo: 3 alunos geravam 1 onibus (41 vazios)
        total = 3
        # Act
        sugestao = combinacao_otima(total, FROTA_SEED)
        # Assert
        self.assertEqual(sugestao, [{"tipo": "VAN", "qtd": 1}])

    def test_sobra_pequena_nao_vira_onibus_extra(self):
        # Arrange — bug antigo: 47 alunos geravam 2 onibus (88 assentos)
        total = 47
        # Act
        sugestao = combinacao_otima(total, FROTA_SEED)
        # Assert
        self.assertEqual(sugestao, [{"tipo": "ONIBUS", "qtd": 1}, {"tipo": "VAN", "qtd": 1}])

    def test_combinacao_nao_gulosa_e_encontrada(self):
        # Arrange — guloso daria 2 onibus + van (103); otimo e onibus + micro (72)
        total = 60
        # Act
        sugestao = combinacao_otima(total, FROTA_SEED)
        # Assert
        self.assertEqual(sugestao, [{"tipo": "ONIBUS", "qtd": 1}, {"tipo": "MICRO", "qtd": 1}])

    def test_respeita_unidades_disponiveis(self):
        # Arrange — sem limite, 90 alunos dariam 6 vans; so existe 1 van
        total = 90
        # Act
        sugestao = combinacao_otima(total, FROTA_SEED)
        # Assert
        qtd = {item["tipo"]: item["qtd"] for item in sugestao}
        self.assertLessEqual(qtd.get("ONIBUS", 0), 2)
        self.assertLessEqual(qtd.get("MICRO", 0), 1)
        self.assertLessEqual(qtd.get("VAN", 0), 1)
        self.assertGreaterEqual(assentos(sugestao, FROTA_SEED), total)

    def test_tipo_sem_unidade_ativa_nao_e_sugerido(self):
        # Arrange — van inativa (0 unidades)
        frota = [("ONIBUS", 44, 2), ("MICRO", 28, 1), ("VAN", 15, 0)]
        # Act
        sugestao = combinacao_otima(10, frota)
        # Assert
        self.assertEqual(sugestao, [{"tipo": "MICRO", "qtd": 1}])

    def test_demanda_acima_da_frota_cobre_todos_os_alunos(self):
        # Arrange — frota total = 131 assentos
        total = 200
        # Act
        sugestao = combinacao_otima(total, FROTA_SEED)
        # Assert
        self.assertGreaterEqual(assentos(sugestao, FROTA_SEED), total)

    def test_empate_de_assentos_prefere_menos_veiculos(self):
        # Arrange — 30 assentos: 1 veiculo de 30 ou 2 de 15
        frota = [("ONIBUS", 30, None), ("VAN", 15, None)]
        # Act
        sugestao = combinacao_otima(30, frota)
        # Assert
        self.assertEqual(sugestao, [{"tipo": "ONIBUS", "qtd": 1}])

    def test_ociosidade_minima_para_todas_as_demandas_da_frota(self):
        # Arrange — forca bruta independente sobre a frota do seed
        frota = FROTA_SEED
        for total in range(1, 132):
            minimo = min(
                o * 44 + m * 28 + v * 15
                for o, m, v in itertools.product(range(3), range(2), range(2))
                if o * 44 + m * 28 + v * 15 >= total
            )
            # Act
            sugestao = combinacao_otima(total, frota)
            # Assert
            self.assertEqual(assentos(sugestao, frota), minimo, f"total={total}")


if __name__ == "__main__":
    unittest.main()
