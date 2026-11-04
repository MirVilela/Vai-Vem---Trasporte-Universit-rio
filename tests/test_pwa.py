"""
Testes AAA dos arquivos do PWA (RNF01 instalacao / RNF02 offline).
O index.html referencia 'manifest.json' e registra 'sw.js' relativos a '/',
entao os dois precisam responder na raiz do site.
"""
import json
import unittest

from apoio import TesteComBanco


class TestArquivosPwa(TesteComBanco):

    def test_service_worker_servido_na_raiz(self):
        # Arrange / Act
        resp = self.cliente.get("/sw.js")
        # Assert
        self.assertEqual(resp.status_code, 200)
        self.assertIn("javascript", resp.content_type)

    def test_service_worker_nao_fica_em_cache_http(self):
        # Arrange / Act — sem isso o navegador pode demorar a pegar versao nova do SW
        resp = self.cliente.get("/sw.js")
        # Assert
        self.assertEqual(resp.headers.get("Cache-Control"), "no-cache")

    def test_manifest_servido_na_raiz_e_valido(self):
        # Arrange / Act
        resp = self.cliente.get("/manifest.json")
        # Assert
        self.assertEqual(resp.status_code, 200)
        manifest = json.loads(resp.get_data(as_text=True))
        self.assertEqual(manifest["start_url"], "/")

    def test_arquivos_pre_cacheados_pelo_sw_existem(self):
        # Arrange — cache.addAll falha inteiro se UM arquivo der 404
        sw = self.cliente.get("/sw.js").get_data(as_text=True)
        bloco = sw.split("const ASSETS = [")[1].split("]")[0]
        assets = [a.strip().strip("'\"") for a in bloco.split(",") if a.strip()]
        # Act
        status = {a: self.cliente.get(a).status_code for a in assets}
        # Assert
        self.assertTrue(assets)
        self.assertEqual(status, {a: 200 for a in assets})

    def test_service_worker_nao_intercepta_api(self):
        # Arrange — o motorista depende do fetch falhar para enfileirar check-ins offline
        sw = self.cliente.get("/sw.js").get_data(as_text=True)
        # Act
        trecho_api = sw.split("url.pathname.startsWith('/api/')")[1].split("}")[0]
        # Assert
        self.assertIn("return;", trecho_api)
        self.assertNotIn("respondWith", trecho_api)


if __name__ == "__main__":
    unittest.main()
