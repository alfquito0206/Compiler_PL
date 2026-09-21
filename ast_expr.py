class AST:
    # clase abstracta: Numero (hojas) y Operacion (nodos) la implementan
    def __init__(self):
        pass

    def mostrar(self):
        # muestra la expresion utilizando parentesis
        raise NotImplementedError

    def mostrar_sin_parentesis(self):
        # muestra la expresion sin parentesis innecesarios
        raise NotImplementedError

    def numero_operaciones(self):
        # devuelve el numero de operaciones de la expresion
        raise NotImplementedError

    def interpreta(self):
        # evalua la expresion
        raise NotImplementedError


class Numero(AST):
    # p.e. para crear una hoja con el digito 7 haríamos Numero(7)
    def __init__(self, valor):
        self.valor = valor

    def mostrar(self):
        return str(self.valor)

    def mostrar_sin_parentesis(self):
        return str(self.valor)

    def numero_operaciones(self):
        # una hoja no es una operacion
        return 0

    def interpreta(self):
        return self.valor


class Operacion(AST):
    # p.e. para crear un nodo con la expresion 5*3 haríamos
    # Operacion('*', Numero(5), Numero(3))

    # prioridad de cada operador: mayor numero, mas prioridad
    PRIORIDAD = {'+': 1, '-': 1, '*': 2, '/': 2}

    def __init__(self, op, izda, dcha):
        if op not in self.PRIORIDAD:
            raise ValueError(f"Operador '{op}' no válido (se admite + - * /)")
        self.op = op
        self.izda = izda
        self.dcha = dcha

    def mostrar(self):
        return '(' + self.izda.mostrar() + self.op + self.dcha.mostrar() + ')'

    def _prioridad(self):
        return self.PRIORIDAD[self.op]

    def mostrar_sin_parentesis(self):
        izda = self.izda.mostrar_sin_parentesis()
        dcha = self.dcha.mostrar_sin_parentesis()
        mi_prioridad = self._prioridad()

        # hijo izquierdo: solo necesita parentesis si tiene menos prioridad
        # (con la misma se agrupa ya por la izquierda: 10-3-2 es (10-3)-2)
        if isinstance(self.izda, Operacion) and self.izda._prioridad() < mi_prioridad:
            izda = '(' + izda + ')'

        # hijo derecho: necesita parentesis si tiene menos prioridad o la
        # misma (10-(3-2) no es 10-3-2), salvo que el operador sea asociativo
        # y el hijo use ese mismo operador (2+(3+4) es igual que 2+3+4)
        if isinstance(self.dcha, Operacion):
            asociativo = self.op in '+*' and self.dcha.op == self.op
            if self.dcha._prioridad() < mi_prioridad or (
                    self.dcha._prioridad() == mi_prioridad and not asociativo):
                dcha = '(' + dcha + ')'

        return izda + self.op + dcha

    def numero_operaciones(self):
        return 1 + self.izda.numero_operaciones() + self.dcha.numero_operaciones()

    def interpreta(self):
        izda = self.izda.interpreta()
        dcha = self.dcha.interpreta()
        if self.op == '+':
            return izda + dcha
        if self.op == '-':
            return izda - dcha
        if self.op == '*':
            return izda * dcha
        return izda / dcha


if __name__ == "__main__":
    # Programa principal
    # Introducimos el arbol de la expresion 4*5+3*2
    num1 = Numero(4)
    num2 = Numero(5)
    num3 = Numero(3)
    num4 = Numero(2)
    arbol1 = Operacion('*', num1, num2)         # 4*5
    arbol2 = Operacion('*', num3, num4)         # 3*2
    arbol_final = Operacion('+', arbol1, arbol2)  # arbol1+arbol2

    # Accedemos al arbol de varias formas mediante funciones miembro
    print('El árbol contiene la expresión:', arbol_final.mostrar())
    print('Sin paréntesis innecesarios:', arbol_final.mostrar_sin_parentesis())
    print('El árbol contiene en total %d operaciones' % arbol_final.numero_operaciones())
    print('La expresión se evalua como:', arbol_final.interpreta())

    # Restas y divisiones, y paréntesis que SI son necesarios
    print()
    pruebas = [
        # (2+3)*4
        Operacion('*', Operacion('+', Numero(2), Numero(3)), Numero(4)),
        # 10-3-2, que es (10-3)-2
        Operacion('-', Operacion('-', Numero(10), Numero(3)), Numero(2)),
        # 10-(3-2)
        Operacion('-', Numero(10), Operacion('-', Numero(3), Numero(2))),
        # 8/(4/2)
        Operacion('/', Numero(8), Operacion('/', Numero(4), Numero(2))),
        # 2+(3+4), asociativa: se puede quitar
        Operacion('+', Numero(2), Operacion('+', Numero(3), Numero(4))),
        # 2+3*4
        Operacion('+', Numero(2), Operacion('*', Numero(3), Numero(4))),
    ]
    for expr in pruebas:
        print(f"{expr.mostrar():<16} -> {expr.mostrar_sin_parentesis():<10} "
              f"= {expr.interpreta()}")
