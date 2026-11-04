"""
Testes AAA do login CPF + PIN (RF01, RS01) e da seguranca do PIN (S01).
"""
import hashlib
import unittest

from apoio import TesteComBanco, app

CPF_JOAO = "12345678901"  # seed: PIN 1234


class TestLogin(TesteComBanco):

    def login(self, cpf, pin):
        return self.cliente.post("/api/login", json={"cpf": cpf, "pin": pin})

    def test_login_valido_retorna_dados_do_aluno(self):
        # Arrange
        cpf, pin = CPF_JOAO, "1234"
        # Act
        resp = self.login(cpf, pin)
        # Assert
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["aluno"]["nome"], "Joao Silva")

    def test_pin_errado_retorna_401(self):
        # Arrange
        cpf, pin = CPF_JOAO, "9999"
        # Act
        resp = self.login(cpf, pin)
        # Assert
        self.assertEqual(resp.status_code, 401)

    def test_cpf_com_formato_invalido_retorna_400(self):
        # Arrange
        cpf = "123.456.789-01"
        # Act
        resp = self.login(cpf, "1234")
        # Assert
        self.assertEqual(resp.status_code, 400)

    def test_pin_com_formato_invalido_retorna_400(self):
        # Arrange
        pin = "12a4"
        # Act
        resp = self.login(CPF_JOAO, pin)
        # Assert
        self.assertEqual(resp.status_code, 400)


class TestSegurancaPin(TesteComBanco):

    def test_pin_salvo_com_pbkdf2_e_salt(self):
        # Arrange / Act
        armazenado = self.consultar_sql("SELECT pin FROM alunos WHERE cpf=?", (CPF_JOAO,))["pin"]
        # Assert
        self.assertTrue(armazenado.startswith("pbkdf2_sha256$"))
        self.assertNotEqual(armazenado, hashlib.sha256(b"1234").hexdigest())

    def test_pins_iguais_geram_hashes_diferentes(self):
        # Arrange
        pin = "1234"
        # Act
        h1, h2 = app.hash_pin(pin), app.hash_pin(pin)
        # Assert
        self.assertNotEqual(h1, h2)
        self.assertTrue(app.verificar_pin(pin, h1))
        self.assertTrue(app.verificar_pin(pin, h2))

    def test_hash_legado_sha256_continua_aceito_e_e_migrado(self):
        # Arrange — aluno gravado no formato antigo (SHA-256 sem salt)
        legado = hashlib.sha256(b"1234").hexdigest()
        self.executar_sql("UPDATE alunos SET pin=? WHERE cpf=?", (legado, CPF_JOAO))
        # Act
        resp = self.cliente.post("/api/login", json={"cpf": CPF_JOAO, "pin": "1234"})
        # Assert
        self.assertEqual(resp.status_code, 200)
        novo = self.consultar_sql("SELECT pin FROM alunos WHERE cpf=?", (CPF_JOAO,))["pin"]
        self.assertTrue(novo.startswith("pbkdf2_sha256$"))
        self.assertTrue(app.verificar_pin("1234", novo))

    def test_hash_legado_com_pin_errado_nao_e_migrado(self):
        # Arrange
        legado = hashlib.sha256(b"1234").hexdigest()
        self.executar_sql("UPDATE alunos SET pin=? WHERE cpf=?", (legado, CPF_JOAO))
        # Act
        resp = self.cliente.post("/api/login", json={"cpf": CPF_JOAO, "pin": "0000"})
        # Assert
        self.assertEqual(resp.status_code, 401)
        atual = self.consultar_sql("SELECT pin FROM alunos WHERE cpf=?", (CPF_JOAO,))["pin"]
        self.assertEqual(atual, legado)


class TestBloqueioTentativas(TesteComBanco):

    def errar(self, vezes):
        for _ in range(vezes):
            self.cliente.post("/api/login", json={"cpf": CPF_JOAO, "pin": "9999"})

    def test_bloqueia_apos_limite_de_falhas_mesmo_com_pin_certo(self):
        # Arrange
        self.errar(app.LOGIN_MAX_FALHAS)
        # Act
        resp = self.cliente.post("/api/login", json={"cpf": CPF_JOAO, "pin": "1234"})
        # Assert
        self.assertEqual(resp.status_code, 429)
        self.assertIn("Tente novamente", resp.get_json()["erro"])

    def test_falhas_abaixo_do_limite_nao_bloqueiam(self):
        # Arrange
        self.errar(app.LOGIN_MAX_FALHAS - 1)
        # Act
        resp = self.cliente.post("/api/login", json={"cpf": CPF_JOAO, "pin": "1234"})
        # Assert
        self.assertEqual(resp.status_code, 200)

    def test_login_certo_zera_contador_de_falhas(self):
        # Arrange
        self.errar(app.LOGIN_MAX_FALHAS - 1)
        self.cliente.post("/api/login", json={"cpf": CPF_JOAO, "pin": "1234"})
        self.errar(app.LOGIN_MAX_FALHAS - 1)
        # Act
        resp = self.cliente.post("/api/login", json={"cpf": CPF_JOAO, "pin": "1234"})
        # Assert
        self.assertEqual(resp.status_code, 200)

    def test_bloqueio_de_um_cpf_nao_afeta_outro(self):
        # Arrange
        self.errar(app.LOGIN_MAX_FALHAS)
        # Act — Maria (seed: PIN 5678)
        resp = self.cliente.post("/api/login", json={"cpf": "98765432100", "pin": "5678"})
        # Assert
        self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
