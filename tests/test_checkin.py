"""
Testes AAA do check-in dinamico do motorista (RF05, RS04, RN01).
"""
import unittest

from apoio import ADMIN, TesteComBanco

DATA = "2026-10-29"
ALUNOS = ["12345678901", "98765432100", "11122233344"]  # seed


class TestCheckin(TesteComBanco):

    def setUp(self):
        super().setUp()
        # Veiculo pequeno para forcar lotacao
        self.executar_sql(
            "INSERT INTO veiculos (id, nome, tipo, capacidade) VALUES ('VAN-TESTE', 'Van Teste', 'VAN', 2)")

    def checkin(self, cpf, veiculo="VAN-TESTE", headers=ADMIN):
        return self.cliente.post("/api/checkin", headers=headers, json={
            "cpf": cpf, "veiculo_id": veiculo, "data": DATA, "tipo": "VOLTA"})

    def test_checkin_valido_desconta_uma_vaga(self):
        # Arrange
        cpf = ALUNOS[0]
        # Act
        resp = self.checkin(cpf)
        # Assert
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["vagas_restantes"], 1)

    def test_veiculo_lotado_rejeita_proximo_passageiro(self):
        # Arrange
        self.checkin(ALUNOS[0])
        self.checkin(ALUNOS[1])
        # Act
        resp = self.checkin(ALUNOS[2])
        # Assert
        self.assertEqual(resp.status_code, 409)
        self.assertIn("lotado", resp.get_json()["erro"])

    def test_checkin_duplicado_e_rejeitado(self):
        # Arrange
        self.checkin(ALUNOS[0])
        # Act
        resp = self.checkin(ALUNOS[0])
        # Assert
        self.assertEqual(resp.status_code, 409)

    def test_veiculo_inexistente_retorna_404(self):
        # Arrange / Act
        resp = self.checkin(ALUNOS[0], veiculo="NAO-EXISTE")
        # Assert
        self.assertEqual(resp.status_code, 404)

    def test_sem_token_admin_retorna_403(self):
        # Arrange / Act
        resp = self.checkin(ALUNOS[0], headers={})
        # Assert
        self.assertEqual(resp.status_code, 403)


if __name__ == "__main__":
    unittest.main()
