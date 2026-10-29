#!/usr/bin/env python
"""Analizador léxico carácter a carácter del lenguaje."""

import argparse
import sys
from pathlib import Path

import componentes
import flujo


class AnalizadorLexico:
    """Convierte caracteres fuente en instancias de ``componentes.Token``."""

    PALABRAS_RESERVADAS = frozenset({
        "PROGRAMA", "VAR", "ENTERO", "REAL", "BOOLEANO", "INICIO", "FIN",
        "SI", "ENTONCES", "SINO", "MIENTRAS", "HACER", "LEE", "ESCRIBE",
        "Y", "O", "NO", "CIERTO", "FALSO",
    })

    # Compatibility with the original skeleton, which exposed ``PR``.
    PR = PALABRAS_RESERVADAS

    def __init__(self, flujo_entrada):
        self.flujo = flujo_entrada
        self.errores = 0

    def _linea(self):
        """Devuelve la línea actual usando cualquiera de las APIs de Flujo."""
        for nombre in ("GetNumLine", "getNumLinea"):
            metodo = getattr(self.flujo, nombre, None)
            if metodo is not None:
                return metodo()
        raise AttributeError("El flujo no proporciona el numero de linea")

    def _leer(self):
        """Lee un carácter y avanza en el flujo de entrada."""
        for nombre in ("NewChar", "newChar", "siguiente"):
            metodo = getattr(self.flujo, nombre, None)
            if metodo is not None:
                return metodo()
        raise AttributeError("El flujo no proporciona una operacion de lectura")

    def _devolver(self):
        """Devuelve el último carácter para que otro estado lo procese."""
        for nombre in ("ReturnChar", "returnChar", "devolver"):
            metodo = getattr(self.flujo, nombre, None)
            if metodo is not None:
                return metodo()
        raise AttributeError("El flujo no proporciona una operacion de devolucion")

    def _error(self, mensaje, linea):
        self.errores += 1
        print(f"ERROR LEXICO (linea {linea}): {mensaje}")

    def _saltar_blancos(self):
        """Ignora espacios; Flujo actualiza la línea al leer '\\n'."""
        while True:
            caracter = self._leer()
            if not caracter:
                return
            if caracter not in " \t\f\r\n":
                self._devolver()
                return

    def _leer_comentario(self):
        """Consume caracteres después de ``%%`` hasta el salto de línea o EOF."""
        while True:
            caracter = self._leer()
            if not caracter or caracter == "\n":
                return

    def _leer_identificador(self, primer_caracter, linea):
        """Lee una letra seguida de cero o más letras o dígitos."""
        texto = primer_caracter
        while True:
            caracter = self._leer()
            if caracter and caracter.isalnum():
                texto += caracter
            else:
                if caracter:
                    self._devolver()
                break

        if texto in self.PALABRAS_RESERVADAS:
            return componentes.PR(texto, linea)
        return componentes.Identif(texto, linea)

    def _leer_numero(self, primer_caracter, linea):
        """Lee un entero o real con la forma dígitos[.dígitos]."""
        texto = primer_caracter
        while True:
            caracter = self._leer()
            if caracter and caracter.isdigit():
                texto += caracter
            else:
                if caracter:
                    self._devolver()
                break

        caracter = self._leer()
        if caracter != ".":
            if caracter:
                self._devolver()
            return componentes.Numero(int(texto), linea)

        texto += "."
        caracter = self._leer()
        if not caracter or not caracter.isdigit():
            if caracter:
                self._devolver()
            self._error(f"numero real incompleto: {texto}", linea)
            return None

        texto += caracter
        while True:
            caracter = self._leer()
            if caracter and caracter.isdigit():
                texto += caracter
            else:
                if caracter:
                    self._devolver()
                break
        return componentes.Numero(float(texto), linea)

    def siguiente_componente(self):
        """Devuelve el siguiente token, ignorando espacios y comentarios ``%%``."""
        while True:
            self._saltar_blancos()
            linea = self._linea()
            caracter = self._leer()

            if not caracter:
                return componentes.EOF(linea)
            if caracter.isalpha():
                return self._leer_identificador(caracter, linea)
            if caracter.isdigit():
                numero = self._leer_numero(caracter, linea)
                if numero is not None:
                    return numero
                continue

            if caracter == "%":
                siguiente = self._leer()
                if siguiente == "%":
                    self._leer_comentario()
                    continue
                if siguiente:
                    self._devolver()
                return componentes.OpMult("SimMod", linea)

            if caracter in "+-":
                nombres = {"+": "SimSuma", "-": "SimResta"}
                return componentes.OpAdd(nombres[caracter], linea)
            if caracter in "*/":
                nombres = {"*": "SimMult", "/": "SimDiv"}
                return componentes.OpMult(nombres[caracter], linea)

            if caracter in "<>":
                siguiente = self._leer()
                operador = caracter
                if siguiente and siguiente in "=>":
                    operador += siguiente
                elif siguiente:
                    self._devolver()
                nombres = {
                    "<": "SimMenor", "<=": "SimMenIgual",
                    ">": "SimMayor", ">=": "SimMayIgual",
                    "<>": "SimDist",
                }
                if operador not in nombres:
                    self._error(
                        f"operador relacional no válido: {operador!r}",
                        linea,
                    )
                    continue
                return componentes.OpRel(nombres[operador], linea)
            if caracter == "=":
                siguiente = self._leer()
                if siguiente and siguiente in "<=>":
                    self._error(
                        f"operador relacional no válido: {'=' + siguiente!r}",
                        linea,
                    )
                    continue
                if siguiente:
                    self._devolver()
                return componentes.OpRel("SimIgual", linea)

            if caracter == ":":
                siguiente = self._leer()
                if siguiente == "=":
                    return componentes.OpAsigna(linea)
                if siguiente:
                    self._devolver()
                return componentes.DosPtos(linea)

            simbolos = {
                ";": componentes.PtoComa,
                ",": componentes.Coma,
                "(": componentes.ParentAp,
                ")": componentes.ParentCi,
                ".": componentes.Punto,
            }
            clase_simbolo = simbolos.get(caracter)
            if clase_simbolo is not None:
                return clase_simbolo(linea)

            self._error(f"caracter no permitido: {caracter!r}", linea)

    # Nombres utilizados habitualmente por los esqueletos proporcionados.
    Analiza = siguiente_componente
    analiza = siguiente_componente


# Nombre compatible con el punto de entrada original de la línea de comandos.
Analex = AnalizadorLexico


def _ruta_fichero(argumento):
    """Resuelve una ruta absoluta o relativa al directorio actual/proyecto."""
    ruta = Path(argumento).expanduser()
    if ruta.is_absolute():
        return ruta.resolve()

    ruta_actual = (Path.cwd() / ruta).resolve()
    if ruta_actual.exists():
        return ruta_actual

    return (Path(__file__).resolve().parent / ruta).resolve()


def _obtener_argumentos():
    """Obtiene el fichero fuente desde la línea de comandos o por teclado."""
    parser = argparse.ArgumentParser(
        description="Analiza léxicamente un fichero del lenguaje de la práctica."
    )
    parser.add_argument(
        "fichero",
        nargs="?",
        help="ruta del fichero fuente; puede ser relativa o absoluta",
    )
    argumentos = parser.parse_args()

    nombre = argumentos.fichero
    if not nombre:
        nombre = input(
            "Introduce la ruta del fichero fuente "
            "(por ejemplo, Prueba1.eje): "
        ).strip()

    if not nombre:
        parser.error("debes indicar un fichero fuente")

    return _ruta_fichero(nombre)


if __name__ == "__main__":
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8")

    fichero = _obtener_argumentos()
    if not fichero.is_file():
        raise SystemExit(
            f"ERROR: no se encontró el fichero fuente:\n{fichero}\n"
            "Comprueba la ruta e inténtalo de nuevo."
        )

    try:
        flujo_entrada = flujo.Flujo(str(fichero))
    except OSError as error:
        raise SystemExit(f"ERROR: no se pudo abrir el fichero: {error}") from error

    analizador = AnalizadorLexico(flujo_entrada)
    print(f"PROGRAMA FUENTE: {fichero}")
    while True:
        token = analizador.siguiente_componente()
        print(token)
        if isinstance(token, componentes.EOF):
            break
    if analizador.errores:
        print(f"Errores lexicos: {analizador.errores}")
        