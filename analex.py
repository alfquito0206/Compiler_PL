#!/usr/bin/env python

"""Analizador léxico del lenguaje de la práctica."""

from sys import argv

import componentes
import flujo


class Analex:
    PR = frozenset({
        "PROGRAMA", "VAR", "ENTERO", "INTEGER", "REAL", "BOOLEANO", "INICIO", "FIN",
        "SI", "ENTONCES", "SINO", "MIENTRAS", "HACER", "LEE", "ESCRIBE",
        "Y", "O", "NO", "CIERTO", "FALSO",
    })

    def __init__(self, flujo_entrada):
        self.flujo = flujo_entrada
        self.poserror = 0
        self.nlinea = self._linea()

    def _linea(self):
        """Obtiene la línea actual, admitiendo las variantes de ``Flujo``."""
        for nombre in ("GetNumLine", "getNumLinea"):
            metodo = getattr(self.flujo, nombre, None)
            if metodo is not None:
                return metodo()
        return self.nlinea

    def _siguiente(self):
        for nombre in ("NewChar", "newChar", "siguiente"):
            metodo = getattr(self.flujo, nombre, None)
            if metodo is not None:
                return metodo()
        raise AttributeError("El flujo no proporciona una operación de lectura")

    def _devolver(self):
        for nombre in ("ReturnChar", "returnChar", "devolver"):
            metodo = getattr(self.flujo, nombre, None)
            if metodo is not None:
                return metodo()
        raise AttributeError("El flujo no proporciona una operación de devolución")

    def _error(self, mensaje, linea):
        print(f"ERROR LÉXICO Línea {linea} :: {mensaje}")

    def TrataNum(self, flujo_entrada, ch, nl=None):
        """Lee un entero o real comenzando por ``ch``."""
        if nl is None:
            nl = self._linea()
        texto = ch
        while True:
            siguiente = self._siguiente()
            if siguiente.isdigit():
                texto += siguiente
            else:
                if siguiente:
                    self._devolver()
                break

        es_real = False
        siguiente = self._siguiente()
        if siguiente == ".":
            es_real = True
            texto += siguiente
            siguiente = self._siguiente()
            if not siguiente.isdigit():
                if siguiente:
                    self._devolver()
                self._error(f"Número real incompleto '{texto}'", nl)
                return None
            texto += siguiente
            while True:
                siguiente = self._siguiente()
                if siguiente.isdigit():
                    texto += siguiente
                else:
                    if siguiente:
                        self._devolver()
                    break
        elif siguiente:
            self._devolver()

        return componentes.Numero(float(texto) if es_real else int(texto), nl)

    def TrataIdent(self, flujo_entrada, ch, nl=None):
        """Lee un identificador o una palabra reservada."""
        if nl is None:
            nl = self._linea()
        texto = ch
        while True:
            siguiente = self._siguiente()
            if siguiente.isalnum() or siguiente == "_":
                texto += siguiente
            else:
                if siguiente:
                    self._devolver()
                break
        if texto in self.PR:
            return componentes.PR(texto, nl)
        return componentes.Identif(texto, nl)

    def TrataComent(self, flujo_entrada=None):
        """Descarta un comentario ``//`` o ``/* ... */``."""
        siguiente = self._siguiente()
        if siguiente == "/":
            while True:
                ch = self._siguiente()
                if not ch or ch == "\n":
                    if ch:
                        self._devolver()
                    return
        if siguiente == "*":
            anterior = ""
            while True:
                ch = self._siguiente()
                if not ch:
                    self._error("Comentario sin cerrar", self._linea())
                    return
                if anterior == "*" and ch == "/":
                    return
                anterior = ch
        if siguiente:
            self._devolver()

    def EliminaBlancos(self, flujo_entrada=None):
        """Consume espacios, tabuladores y saltos de línea."""
        while True:
            ch = self._siguiente()
            if not ch:
                return
            if ch in " \t\f\r":
                continue
            if ch == "\n":
                continue
            if ch:
                self._devolver()
            return

    def Analiza(self):
        while True:
            self.EliminaBlancos()
            nl = self._linea()
            ch = self._siguiente()

            if not ch:
                return componentes.EOF(nl)
            if ch.isdigit():
                token = self.TrataNum(self.flujo, ch, nl)
                if token is not None:
                    return token
                continue
            if ch.isalpha() or ch == "_":
                return self.TrataIdent(self.flujo, ch, nl)

            if ch == ":":
                siguiente = self._siguiente()
                if siguiente == "=":
                    return componentes.OpAsigna(nl)
                if siguiente:
                    self._devolver()
                return componentes.DosPtos(nl)
            if ch in "+-":
                return componentes.OpAdd({"+": "SimSuma", "-": "SimResta"}[ch], nl)
            if ch in "*/":
                siguiente = self._siguiente()
                if ch == "/" and siguiente and siguiente in "/*":
                    self._devolver()
                    self.TrataComent(self.flujo)
                    continue
                if siguiente:
                    self._devolver()
                return componentes.OpMult({"*": "SimMult", "/": "SimDiv"}[ch], nl)
            if ch in "<>":
                siguiente = self._siguiente()
                op = ch
                if siguiente and siguiente in "=>":
                    op += siguiente
                elif siguiente:
                    self._devolver()
                nombres = {
                    "=": "SimIgual", "<>": "SimDist", "<": "SimMenor",
                    "<=": "SimMenIgual", ">": "SimMayor", ">=": "SimMayIgual",
                }
                return componentes.OpRel(nombres[op], nl)
            if ch == "=":
                return componentes.OpRel("SimIgual", nl)
            puntuacion = {
                ";": componentes.PtoComa,
                ",": componentes.Coma,
                ":": componentes.DosPtos,
                "(": componentes.ParentAper,
                ")": componentes.ParentCi,
                ".": componentes.Punto,
            }
            if ch in puntuacion:
                return puntuacion[ch](nl)
            if ch == "#":
                while True:
                    siguiente = self._siguiente()
                    if not siguiente or siguiente == "\n":
                        if siguiente:
                            self._devolver()
                        break
                continue

            self._error(f"Caracter '{ch}' invalido", nl)


if __name__ == "__main__":
    if len(argv) != 2:
        raise SystemExit(f"Uso: {argv[0]} FICHERO")
    nombre = argv[1]
    print(f"PROGRAMA FUENTE {nombre!r}")
    analex = Analex(flujo.Flujo(nombre))
    componente = analex.Analiza()
    while componente.cat != "EOF":
        print(componente)
        componente = analex.Analiza()
