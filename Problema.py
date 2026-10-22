class Flujo:
    def __init__(self, datos_vector):
        self.datos = datos_vector
        self.posicion = 0
        self.linea_actual = 1
        self.columna_actual = 0
        self.historial = []

    def NewChar(self):
        if self.posicion >= len(self.datos):
            return None

        self.historial.append(
            (self.posicion, self.linea_actual, self.columna_actual)
        )
        char = self.datos[self.posicion]
        self.posicion += 1

        if char == '\n':
            self.linea_actual += 1
            self.columna_actual = 0
        else:
            self.columna_actual += 1

        return char

    def ReturnChar(self):
        if not self.historial:
            return None

        posicion, linea, columna = self.historial.pop()
        char = self.datos[posicion]
        self.posicion = posicion
        self.linea_actual = linea
        self.columna_actual = columna
        return char

    def GetNumLine(self):
        return self.linea_actual

    def GetCharInLine(self):
        return self.columna_actual
class Arbol:
    def __init__(self, elto, valor=None, tipo=None):
        """
        Constructor que recibe la información del nodo raíz.
        El árbol vacío se representa con subárboles en None.
        """
        self.elto = elto
        self.atributos = {'valor': valor, 'tipo': tipo}
        self.izdo = None
        self.dcho = None

    def Insert(self, elto, valor=None, tipo=None):
        """Inserta un elemento manteniendo la propiedad del árbol binario de búsqueda."""
        if elto < self.elto:
            if self.izdo is None:
                self.izdo = Arbol(elto, valor, tipo)
            else:
                self.izdo.Insert(elto, valor, tipo)
        elif elto > self.elto:
            if self.dcho is None:
                self.dcho = Arbol(elto, valor, tipo)
            else:
                self.dcho.Insert(elto, valor, tipo)
        else:
            # No permitimos repeticiones
            print(f"El identificador '{elto}' ya se encuentra en el árbol.")

    def Exists(self, elto):
        """Comprueba recursivamente si un elemento se encuentra en el árbol."""
        if elto == self.elto:
            return True
        elif elto < self.elto and self.izdo is not None:
            return self.izdo.Exists(elto)
        elif elto > self.elto and self.dcho is not None:
            return self.dcho.Exists(elto)
        return False

    def ModifyAttr(self, elto, atributo, nuevo_valor):
        """Modifica el valor del atributo indicado para el identificador dado."""
        if elto == self.elto:
            if atributo in self.atributos:
                self.atributos[atributo] = nuevo_valor
        elif elto < self.elto and self.izdo is not None:
            self.izdo.ModifyAttr(elto, atributo, nuevo_valor)
        elif elto > self.elto and self.dcho is not None:
            self.dcho.ModifyAttr(elto, atributo, nuevo_valor)

    def GetValue(self, elto, atributo):
        """Devuelve el valor del atributo indicado para el identificador dado."""
        if elto == self.elto:
            return self.atributos.get(atributo)
        elif elto < self.elto and self.izdo is not None:
            return self.izdo.GetValue(elto, atributo)
        elif elto > self.elto and self.dcho is not None:
            return self.dcho.GetValue(elto, atributo)
        return None

    def __str__(self, nivel=0):
        """Devuelve una representación apropiada del árbol con indentación."""
        representacion = ""
        # Recorrido in-order inverso para imprimir de forma horizontal
        if self.dcho is not None:
            representacion += self.dcho.__str__(nivel + 1)
        representacion += "    " * nivel + str(self.elto) + "\n"
        if self.izdo is not None:
            representacion += self.izdo.__str__(nivel + 1)
        return representacion

class AST:
    def __init__(self): pass
    def mostrar(self): pass
    def numero_operaciones(self): pass
    def interpreta(self): pass

class Numero(AST):
    def __init__(self, valor):
        self.valor = valor

    def mostrar(self):
        return str(self.valor)

    def numero_operaciones(self):
        return 0

    def interpreta(self):
        return self.valor
        
    def prioridad(self):
        return 100 # Un número tiene la máxima prioridad (sin paréntesis)

class Operacion(AST):
    def __init__(self, op, izda, dcha):
        self.op = op
        self.izda = izda
        self.dcha = dcha

    def prioridad(self):
        """Asigna precedencia a los operadores para saber cuándo poner paréntesis."""
        if self.op in ('+', '-'): return 1
        if self.op in ('*', '/'): return 2
        return 0

    def mostrar(self):
        """Muestra la expresión omitiendo paréntesis innecesarios."""
        izda_str = self.izda.mostrar()
        dcha_str = self.dcha.mostrar()

        # Si la operación hija izquierda tiene menor prioridad, necesita paréntesis
        if isinstance(self.izda, Operacion) and self.izda.prioridad() < self.prioridad():
            izda_str = f"({izda_str})"
            
        # Si la operación derecha tiene menor o *igual* prioridad (por asociatividad en restas/divisiones)
        if isinstance(self.dcha, Operacion) and self.dcha.prioridad() <= self.prioridad():
            dcha_str = f"({dcha_str})"

        return f"{izda_str}{self.op}{dcha_str}"

    def numero_operaciones(self):
        """Cuenta el nodo actual (+1) más los de sus hijos."""
        return 1 + self.izda.numero_operaciones() + self.dcha.numero_operaciones()

    def interpreta(self):
        """Evalúa matemáticamente la expresión recorriendo el AST."""
        val_izda = self.izda.interpreta()
        val_dcha = self.dcha.interpreta()
        
        if self.op == '+': return val_izda + val_dcha
        elif self.op == '-': return val_izda - val_dcha
        elif self.op == '*': return val_izda * val_dcha
        elif self.op == '/': 
            if val_dcha == 0: raise ValueError("División por cero")
            return val_izda / val_dcha

# -- Programa principal de prueba (incluyendo los cambios pedidos) --
if __name__ == "__main__":
    # Expresión original propuesta: 4*5+3*2
    num1 = Numero(4)
    num2 = Numero(5)
    num3 = Numero(3)
    num4 = Numero(2)
    
    arbol1 = Operacion('*', num1, num2) # 4*5
    arbol2 = Operacion('*', num3, num4) # 3*2
    arbol_final = Operacion('+', arbol1, arbol2) # arbol1+arbol2
    
    print('El árbol contiene la expresión:', arbol_final.mostrar())
    print('El árbol contiene en total %d operaciones' % arbol_final.numero_operaciones())
    print('La expresión se evalúa como:', arbol_final.interpreta())
    
    # Prueba adicional para demostrar los paréntesis
    # Expresión: (4+5)*3
    suma = Operacion('+', num1, num2)
    multiplicacion = Operacion('*', suma, num3)
    print("\nEjemplo de paréntesis dinámico:")
    print('Expresión:', multiplicacion.mostrar())
    print('Evaluación:', multiplicacion.interpreta())