"""Verificaciones locales sin credenciales, Internet ni servidores activos.
Desde backend: python -m unittest discover -s tests -v
"""
import re
import unittest
from pathlib import Path

from core.ddl import ddl_create, ddl_indices, ddl_drop, datos_prueba
from core.dcl_config import dcl_usuarios, PERMISOS_OBJETIVO, TABLAS_CONCESIONARIA


class EsquemaConcesionariaTest(unittest.TestCase):
    def test_ocho_tablas_y_indices(self):
        self.assertEqual(set(ddl_create), set(TABLAS_CONCESIONARIA))
        self.assertEqual(len(ddl_indices), 8)
        self.assertEqual(len(ddl_drop), 8)
        self.assertEqual(len(datos_prueba), 8)

    def test_quince_roles_reales(self):
        self.assertEqual(len(dcl_usuarios), 15)
        self.assertEqual(set(dcl_usuarios), set(PERMISOS_OBJETIVO))
        for tabla, accion in PERMISOS_OBJETIVO.values():
            self.assertIn(tabla, TABLAS_CONCESIONARIA)
            self.assertIn(accion, ('SELECT', 'INSERT', 'UPDATE', 'DELETE'))

    def test_mysql_ocho_tablas_en_orden(self):
        sql = (Path(__file__).resolve().parents[1] / 'sql' / 'mysql_concesionaria.sql').read_text(encoding='utf-8')
        self.assertEqual(re.findall(r'CREATE TABLE (\w+)', sql), list(TABLAS_CONCESIONARIA))
        self.assertEqual(sql.count('ENGINE=InnoDB'), 8)


if __name__ == '__main__':
    unittest.main()
