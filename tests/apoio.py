"""
Apoio aos testes: banco SQLite temporario por teste (nunca toca o database.db real).
"""
import os
import sys
import shutil
import logging
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app  # noqa: E402

logging.getLogger("VEM").setLevel(logging.WARNING)

ADMIN = {"X-Admin-Token": app.ADMIN_TOKEN}
FUSO_BR = timezone(timedelta(hours=-3))


def agora_fixo(ano=2026, mes=10, dia=28, hora=10, minuto=0):
    """Datetime 'agora' controlado para testes de horario (fuso de Brasilia)."""
    return datetime(ano, mes, dia, hora, minuto, tzinfo=FUSO_BR)


class TesteComBanco(unittest.TestCase):
    """Cria um banco novo com o seed padrao (init_db) antes de cada teste."""

    def setUp(self):
        self._pasta = tempfile.mkdtemp(prefix="vem_teste_")
        self._db_original = app.DB_PATH
        app.DB_PATH = os.path.join(self._pasta, "teste.db")
        app.init_db()
        app._falhas_login.clear()
        self.cliente = app.app.test_client()

    def tearDown(self):
        app.DB_PATH = self._db_original
        app._falhas_login.clear()
        shutil.rmtree(self._pasta, ignore_errors=True)

    def executar_sql(self, sql, parametros=()):
        conn = app.get_db()
        conn.execute(sql, parametros)
        conn.commit()
        conn.close()

    def consultar_sql(self, sql, parametros=()):
        conn = app.get_db()
        linha = conn.execute(sql, parametros).fetchone()
        conn.close()
        return linha
