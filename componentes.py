#!/usr/bin/env python

"""Categorías léxicas del lenguaje."""


class Componente:
    def __init__(self, linea=0):
        self.cat = self.__class__.__name__
        self.linea = linea

    @property
    def nl(self):
        """Alias compatible con el nombre usado en el enunciado inicial."""
        return self.linea

    def __str__(self):
        atributos = [f"{k}: {v}" for k, v in self.__dict__.items() if k != "cat"]
        return f"{self.__class__.__name__} ({', '.join(atributos)})" \
            if atributos else self.__class__.__name__


class _Puntuacion(Componente):
    pass


class PtoComa(_Puntuacion):
    pass


class Coma(_Puntuacion):
    pass


class DosPtos(_Puntuacion):
    pass


class ParentAper(_Puntuacion):
    pass


class ParentCi(_Puntuacion):
    pass


class Punto(_Puntuacion):
    pass


class OpPunt(_Puntuacion):
    """Compatibilidad para signos de puntuación no especializados."""

    def __init__(self, op, linea=0):
        super().__init__(linea)
        self.valor = op


class OpAsigna(Componente):
    pass


class OpAdd(Componente):
    def __init__(self, op, linea=0):
        self.valor = op
        super().__init__(linea)


class OpMult(Componente):
    def __init__(self, op, linea=0):
        self.valor = op
        super().__init__(linea)


class Numero(Componente):
    def __init__(self, valor, linea=0):
        self.valor = valor
        super().__init__(linea)
        self.tipo = type(valor)


class Identif(Componente):
    def __init__(self, valor, linea=0):
        self.valor = valor
        super().__init__(linea)


class PR(Componente):
    def __init__(self, valor, linea=0):
        self.valor = valor
        super().__init__(linea)


class OpRel(Componente):
    def __init__(self, op, linea=0):
        self.valor = op
        super().__init__(linea)


class EOF(Componente):
    pass
