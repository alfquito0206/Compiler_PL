#!/usr/bin/env python
"""Clases de componentes léxicos utilizadas por el analizador."""


class Token:
    """Información común compartida por todos los componentes léxicos.

    Los símbolos simples no muestran ``linea`` en ``__str__`` porque ese es el
    formato de salida exigido por la práctica. El valor se conserva para que
    las siguientes fases del compilador puedan usarlo en sus diagnósticos.
    """

    def __init__(self, linea=0):
        self.cat = type(self).__name__
        self.linea = linea

    @property
    def nl(self):
        """Alias compatible con código que denomina ``nl`` a la línea."""
        return self.linea

    def __str__(self):
        return self.cat


# The old project used Componente.  Keep the alias so existing imports work.
Componente = Token


class _SimpleSymbol(Token):
    """Token de puntuación u operador sin atributos impresos."""

    def __str__(self):
        return self.cat


class PtoComa(_SimpleSymbol):
    pass


class DosPtos(_SimpleSymbol):
    pass


class Coma(_SimpleSymbol):
    pass


class ParentAp(_SimpleSymbol):
    pass


# Compatibility with the previous misspelled/expanded name.
ParentAper = ParentAp


class ParentCi(_SimpleSymbol):
    pass


class Punto(_SimpleSymbol):
    pass


class OpAsigna(_SimpleSymbol):
    pass


class OpPunt(_SimpleSymbol):
    pass


class PR(Token):
    def __init__(self, valor, linea=0):
        super().__init__(linea)
        self.valor = valor

    def __str__(self):
        return f"PR (valor: {self.valor}, linea: {self.linea})"


class Identif(Token):
    def __init__(self, valor, linea=0):
        super().__init__(linea)
        self.valor = valor

    def __str__(self):
        return f"Identif (valor: {self.valor}, linea: {self.linea})"


class Numero(Token):
    def __init__(self, valor, linea=0):
        super().__init__(linea)
        self.valor = valor
        self.tipo = type(valor)

    def __str__(self):
        return (
            f"Numero (valor: {self.valor}, linea: {self.linea}, "
            f"tipo: {self.tipo})"
        )


class OpRel(Token):
    def __init__(self, op, linea=0):
        super().__init__(linea)
        self.valor = op

    def __str__(self):
        return f"OpRel (valor: {self.valor}, linea: {self.linea})"


class OpAdd(Token):
    def __init__(self, op, linea=0):
        super().__init__(linea)
        self.valor = op

    def __str__(self):
        return f"OpAdd (valor: {self.valor}, linea: {self.linea})"


class OpMult(Token):
    def __init__(self, op, linea=0):
        super().__init__(linea)
        self.valor = op

    def __str__(self):
        return f"OpMult (valor: {self.valor}, linea: {self.linea})"


class EOF(_SimpleSymbol):
    pass
