#!/usr/bin/env python
"""Analizador sintáctico descendente recursivo del lenguaje de la práctica."""

import sys
from pathlib import Path

import analex
import componentes
import flujo


class AnalizadorSintactico:
    """Reconoce programas usando el analizador léxico recibido."""

    INICIO_SENTENCIA = {
        "Identif", "PR:SI", "PR:MIENTRAS", "PR:LEE", "PR:ESCRIBE",
        "PR:INICIO",
    }
    INICIO_EXPRESION = {"Identif", "Numero", "ParentAp", "OpAdd",
                        "PR:NO", "PR:CIERTO", "PR:FALSO"}
    SINCRONIZACION = {"PtoComa", "PR:FIN", "PR:SINO", "EOF"}

    def __init__(self, lexico):
        self.lexico = lexico
        self.errores = 0
        self.token_actual = None
        self.avanza()

    # Obtiene el siguiente componente léxico.
    def avanza(self):
        siguiente = getattr(self.lexico, "siguiente", None)
        if siguiente is None:
            siguiente = getattr(self.lexico, "Analiza", None)
        if siguiente is None:
            raise AttributeError("El analizador léxico no tiene siguiente()")
        self.token_actual = siguiente()
        return self.token_actual

    def _clave(self, token=None):
        token = token or self.token_actual
        if token is None:
            return "EOF"
        categoria = getattr(token, "cat", type(token).__name__)
        valor = getattr(token, "valor", None)
        if categoria == "PR" and valor is not None:
            return f"PR:{valor}"
        return categoria

    def _es(self, esperado):
        if isinstance(esperado, (set, frozenset, tuple, list)):
            return any(self._es(elemento) for elemento in esperado)
        return self._clave() == esperado

    def _nombre_token(self):
        if self.token_actual is None:
            return "fin de archivo"
        valor = getattr(self.token_actual, "valor", None)
        if valor is not None:
            return f"{self._clave()} ({valor})"
        return self._clave()

    # Descarta tokens hasta llegar a un punto seguro de la gramática.
    def sincroniza(self, conjunto_sincronizacion):
        while self._clave() not in conjunto_sincronizacion and not self._es("EOF"):
            self.avanza()

    def _error(self, esperado):
        linea = getattr(self.token_actual, "linea", 0)
        print(
            f"ERROR SINTACTICO (linea {linea}): se esperaba {esperado}; "
            f"se encontró {self._nombre_token()}"
        )
        self.errores += 1

    # Comprueba un terminal y continúa aunque haya un error.
    def comprueba(self, categoria_esperada):
        if self._es(categoria_esperada):
            self.avanza()
            return True
        if isinstance(categoria_esperada, (set, frozenset, tuple, list)):
            esperado = "uno de " + ", ".join(sorted(categoria_esperada))
        else:
            esperado = categoria_esperada
        self._error(esperado)
        self.sincroniza(set(categoria_esperada)
                        if isinstance(categoria_esperada, (set, frozenset))
                        else {categoria_esperada, "EOF"})
        return False

    # <Programa> -> PROGRAMA Identif ; <Declaraciones> INICIO
    #                <ListaSentencias> FIN .
    def analiza_programa(self):
        correcto = True
        correcto = self.comprueba("PR:PROGRAMA") and correcto
        correcto = self.comprueba("Identif") and correcto
        correcto = self.comprueba("PtoComa") and correcto
        self.analiza_declaraciones()
        correcto = self.comprueba("PR:INICIO") and correcto
        self.analiza_lista_sentencias({"PR:FIN"})
        correcto = self.comprueba("PR:FIN") and correcto
        correcto = self.comprueba("Punto") and correcto
        if not self._es("EOF"):
            self._error("EOF")
            self.sincroniza({"EOF"})
            correcto = False
        return correcto and self.errores == 0

    # <Declaraciones> -> VAR <Declaracion> <Declaraciones> | lambda
    def analiza_declaraciones(self):
        while self._es("PR:VAR"):
            self.avanza()
            self.analiza_declaracion()

    # <Declaracion> -> Identif { , Identif } : <Tipo> ;
    def analiza_declaracion(self):
        if not self._es("Identif"):
            self._error("Identif")
            self.sincroniza({"PtoComa", "PR:INICIO", "EOF"})
            if self._es("PtoComa"):
                self.avanza()
            return False
        self.avanza()
        while self._es("Coma"):
            self.avanza()
            self.comprueba("Identif")
        self.comprueba("DosPtos")
        self.analiza_tipo()
        return self.comprueba("PtoComa")

    # <Tipo> -> ENTERO | REAL | BOOLEANO
    def analiza_tipo(self):
        if self._es({"PR:ENTERO", "PR:REAL", "PR:BOOLEANO"}):
            self.avanza()
            return True
        self._error("PR:ENTERO, PR:REAL o PR:BOOLEANO")
        self.sincroniza({"PtoComa", "PR:INICIO", "EOF"})
        return False

    # <ListaSentencias> -> { <Sentencia> ; }.
    def analiza_lista_sentencias(self, siguientes):
        while self._clave() in self.INICIO_SENTENCIA:
            self.analiza_sentencia()
            if not self.comprueba("PtoComa"):
                self.sincroniza(set(siguientes) | self.INICIO_SENTENCIA |
                                {"PtoComa", "EOF"})
                if self._es("PtoComa"):
                    self.avanza()
        # Un punto y coma final es válido antes de FIN o SINO.
        while self._es("PtoComa"):
            self.avanza()

    # <Sentencia> -> Identif := <Expresion> | SI ... | MIENTRAS ...
    #                 | LEE (...) | ESCRIBE (...) | <Bloque>
    def analiza_sentencia(self):
        if self._es("Identif"):
            self.avanza()
            self.comprueba("OpAsigna")
            self.analiza_expresion()
        elif self._es("PR:SI"):
            self.analiza_si()
        elif self._es("PR:MIENTRAS"):
            self.analiza_mientras()
        elif self._es("PR:LEE") or self._es("PR:ESCRIBE"):
            self.analiza_entrada_salida()
        elif self._es("PR:INICIO"):
            self.analiza_bloque()
        else:
            self._error("inicio de sentencia")
            self.sincroniza(self.SINCRONIZACION | self.INICIO_SENTENCIA)

    # <Bloque> -> INICIO <ListaSentencias> FIN
    def analiza_bloque(self):
        self.comprueba("PR:INICIO")
        self.analiza_lista_sentencias({"PR:FIN"})
        self.comprueba("PR:FIN")

    # <Si> -> SI ( <Expresion> ) ENTONCES <Sentencia> [ SINO <Sentencia> ]
    def analiza_si(self):
        self.avanza()
        self.comprueba("ParentAp")
        self.analiza_expresion()
        self.comprueba("ParentCi")
        self.comprueba("PR:ENTONCES")
        self.analiza_sentencia()
        if self._es("PR:SINO"):
            self.avanza()
            self.analiza_sentencia()

    # <Mientras> -> MIENTRAS ( <Expresion> ) HACER <Sentencia>
    def analiza_mientras(self):
        self.avanza()
        self.comprueba("ParentAp")
        self.analiza_expresion()
        self.comprueba("ParentCi")
        self.comprueba("PR:HACER")
        self.analiza_sentencia()

    # <EntradaSalida> -> ( LEE | ESCRIBE ) ( [ <Expresion> ] )
    def analiza_entrada_salida(self):
        self.avanza()
        self.comprueba("ParentAp")
        if self._clave() in self.INICIO_EXPRESION:
            self.analiza_expresion()
        self.comprueba("ParentCi")

    # <Expresion> -> <ExpresionSimple> [ OpRel <ExpresionSimple> ]
    def analiza_expresion(self):
        correcto = self.analiza_expresion_simple()
        if self._es("OpRel"):
            self.avanza()
            correcto = self.analiza_expresion_simple() and correcto
        return correcto

    # <ExpresionSimple> -> [ OpAdd ] <Termino> { OpAdd <Termino> }
    def analiza_expresion_simple(self):
        if self._es("OpAdd"):
            self.avanza()
        correcto = self.analiza_termino()
        while self._es("OpAdd") or self._es("PR:O"):
            self.avanza()
            correcto = self.analiza_termino() and correcto
        return correcto

    # <Termino> -> <Factor> { OpMult <Factor> | Y <Factor> }
    def analiza_termino(self):
        correcto = self.analiza_factor()
        while self._es("OpMult") or self._es("PR:Y"):
            self.avanza()
            correcto = self.analiza_factor() and correcto
        return correcto

    # <Factor> -> Identif | Numero | CIERTO | FALSO | ( <Expresion> )
    #              | NO <Factor>
    def analiza_factor(self):
        if self._es({"Identif", "Numero", "PR:CIERTO", "PR:FALSO"}):
            self.avanza()
            return True
        if self._es("PR:NO"):
            self.avanza()
            return self.analiza_factor()
        if self._es("ParentAp"):
            self.avanza()
            correcto = self.analiza_expresion()
            correcto = self.comprueba("ParentCi") and correcto
            return correcto
        self._error("factor")
        self.sincroniza({"OpAdd", "OpMult", "OpRel", "ParentCi",
                         "PtoComa", "EOF"})
        return False

    # Nombre del esqueleto anterior, conservado para no romper llamadas.
    def Programa(self):
        return self.analiza_programa()


Sintactico = AnalizadorSintactico


def _ruta_fichero(argumento):
    ruta = Path(argumento)
    if ruta.is_absolute():
        return ruta
    return Path(__file__).resolve().parent / ruta


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python anasint.py fichero")
    fichero = _ruta_fichero(sys.argv[1])
    analizador_lexico = analex.AnalizadorLexico(flujo.Flujo(str(fichero)))
    sintactico = AnalizadorSintactico(analizador_lexico)
    if sintactico.analiza_programa():
        print(f"Analisis sintactico SATISFACTORIO. Fichero: {fichero}")
    else:
        print(f"Analisis sintactico CON ERRORES. Fichero: {fichero}")
