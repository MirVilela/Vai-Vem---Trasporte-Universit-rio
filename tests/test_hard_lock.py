"""
Testes AAA do Hard Lock (RS03): corte de horario, trava manual e datas passadas.
Hora "agora" fixada em 28/10/2026 (quarta-feira), fuso de Brasilia.
"""
import unittest
from unittest import mock

from apoio import TesteComBanco, agora_fixo, app

HOJE = "2026-10-28"
AMANHA = "2026-10-29"
ONTEM = "2026-10-27"


class TestHardLock(TesteComBanco):

    def travado(self, data, hora=10, minuto=0):
        with mock.patch.object(app, "get_server_now", return_value=agora_fixo(hora=hora, minuto=minuto)):
            return app.is_hard_locked(data)

    def test_hoje_antes_do_corte_esta_liberado(self):
        # Arrange / Act
        resultado = self.travado(HOJE, hora=13, minuto=59)
        # Assert
        self.assertFalse(resultado)

    def test_hoje_no_horario_de_corte_esta_travado(self):
        # Arrange / Act
        resultado = self.travado(HOJE, hora=14, minuto=0)
        # Assert
        self.assertTrue(resultado)

    def test_amanha_apos_o_corte_continua_liberado(self):
        # Arrange / Act
        resultado = self.travado(AMANHA, hora=23, minuto=59)
        # Assert
        self.assertFalse(resultado)

    def test_data_passada_sempre_travada(self):
        # Arrange
        self.executar_sql("UPDATE configuracoes SET valor='ABERTO' WHERE chave='trava_manual'")
        # Act
        resultado = self.travado(ONTEM)
        # Assert
        self.assertTrue(resultado)

    def test_horario_de_corte_configuravel(self):
        # Arrange
        self.executar_sql("UPDATE configuracoes SET valor='09:30' WHERE chave='horario_corte'")
        # Act
        antes = self.travado(HOJE, hora=9, minuto=29)
        depois = self.travado(HOJE, hora=9, minuto=30)
        # Assert
        self.assertFalse(antes)
        self.assertTrue(depois)

    def test_trava_manual_fechado_bloqueia_datas_futuras(self):
        # Arrange
        self.executar_sql("UPDATE configuracoes SET valor='FECHADO' WHERE chave='trava_manual'")
        # Act
        resultado = self.travado(AMANHA)
        # Assert
        self.assertTrue(resultado)

    def test_trava_manual_aberto_libera_hoje_apos_o_corte(self):
        # Arrange
        self.executar_sql("UPDATE configuracoes SET valor='ABERTO' WHERE chave='trava_manual'")
        # Act
        resultado = self.travado(HOJE, hora=18)
        # Assert
        self.assertFalse(resultado)


class TestReserva(TesteComBanco):

    CPF = "12345678901"

    def reservar(self, reservas, hora=10):
        with mock.patch.object(app, "get_server_now", return_value=agora_fixo(hora=hora)):
            return self.cliente.post("/api/reservar", json={"cpf": self.CPF, "reservas": reservas})

    def test_reserva_para_amanha_e_registrada(self):
        # Arrange
        reservas = [{"data": AMANHA, "ida": 1, "volta": 0}]
        # Act
        resp = self.reservar(reservas)
        # Assert
        self.assertEqual(resp.get_json()["total_registradas"], 1)
        linha = self.consultar_sql("SELECT ida, volta FROM reservas WHERE cpf=? AND data=?", (self.CPF, AMANHA))
        self.assertEqual((linha["ida"], linha["volta"]), (1, 0))

    def test_reserva_para_hoje_apos_corte_e_rejeitada(self):
        # Arrange
        reservas = [{"data": HOJE, "ida": 1, "volta": 1}]
        # Act
        resp = self.reservar(reservas, hora=15)
        # Assert
        self.assertEqual(resp.get_json()["total_registradas"], 0)
        self.assertIsNone(self.consultar_sql("SELECT id FROM reservas WHERE data=?", (HOJE,)))

    def test_nova_reserva_no_mesmo_dia_substitui_a_anterior(self):
        # Arrange — RN: uma reserva ativa por aluno/dia
        self.reservar([{"data": AMANHA, "ida": 1, "volta": 0}])
        # Act
        self.reservar([{"data": AMANHA, "ida": 0, "volta": 1}])
        # Assert
        linha = self.consultar_sql(
            "SELECT COUNT(*) AS n, MAX(ida) AS ida, MAX(volta) AS volta FROM reservas WHERE cpf=? AND data=?",
            (self.CPF, AMANHA))
        self.assertEqual((linha["n"], linha["ida"], linha["volta"]), (1, 0, 1))

    def test_dia_sem_ida_nem_volta_e_ignorado(self):
        # Arrange
        reservas = [{"data": AMANHA, "ida": 0, "volta": 0}]
        # Act
        resp = self.reservar(reservas)
        # Assert
        self.assertEqual(resp.get_json()["total_registradas"], 0)


if __name__ == "__main__":
    unittest.main()
