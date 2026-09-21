class arbol:
    # arbol binario de busqueda ordenado por el nombre del identificador
    # elto: nombre del identificador (es la clave por la que se ordena)
    # atributos: diccionario con valor, tipo, direccion de memoria...
    # izdo, dcho: subarboles; el arbol vacio es None

    def __init__(self, elto, atributos=None):
        if atributos is None:
            atributos = {}
        self.elto = elto
        self.atributos = atributos
        self.izdo = None
        self.dcho = None

    def Insert(self, elto, atributos=None):
        if atributos is None:
            atributos = {}
        # no se permiten repeticiones
        if elto == self.elto:
            print(f"El símbolo '{elto}' ya existe en el árbol.")
            return False
        # menor: subarbol izquierdo, mayor: subarbol derecho
        if elto < self.elto:
            if self.izdo is None:
                self.izdo = arbol(elto, atributos)
                return True
            return self.izdo.Insert(elto, atributos)
        if self.dcho is None:
            self.dcho = arbol(elto, atributos)
            return True
        return self.dcho.Insert(elto, atributos)

    # devuelve el nodo que contiene el identificador, o None si no esta
    def _Buscar(self, elto):
        nodo = self
        while nodo is not None:
            if elto == nodo.elto:
                return nodo
            nodo = nodo.izdo if elto < nodo.elto else nodo.dcho
        return None

    def Exists(self, elto):
        return self._Buscar(elto) is not None

    def ModifyAttr(self, elto, atributo, new_value):
        nodo = self._Buscar(elto)
        if nodo is None:
            print(f"El símbolo '{elto}' no existe en el árbol.")
            return False
        nodo.atributos[atributo] = new_value
        return True

    def GetValue(self, elto, atributo):
        nodo = self._Buscar(elto)
        if nodo is None:
            print(f"El símbolo '{elto}' no existe en el árbol.")
            return None
        return nodo.atributos.get(atributo, None)

    # una linea por nodo, cada nivel de profundidad se sangra 4 espacios
    def __str__(self):
        return "\n".join(self._Lineas(0, ""))

    def _Lineas(self, nivel, etiqueta):
        lineas = ["    " * nivel + etiqueta + f"{self.elto} {self.atributos}"]
        for etiq, hijo in (("izdo: ", self.izdo), ("dcho: ", self.dcho)):
            if hijo is not None:
                lineas += hijo._Lineas(nivel + 1, etiq)
        return lineas


if __name__ == "__main__":
    # la raiz es el primer identificador insertado
    ts = arbol("m", {"tipo": "entero", "valor": 0})

    # 1. Insertar identificadores (izquierda y derecha de la raiz, y mas profundo)
    ts.Insert("c", {"tipo": "real", "valor": 19.99})
    ts.Insert("t", {"tipo": "entero", "valor": 7})
    ts.Insert("a", {"tipo": "entero", "valor": 1})
    ts.Insert("e", {"tipo": "real", "valor": 2.5})
    ts.Insert("z", {"tipo": "entero", "valor": 9})
    print(ts)

    # 2. Comprobar existencia (Exists)
    print(f"¿Existe 'e'?: {ts.Exists('e')}")  # True
    print(f"¿Existe 'k'?: {ts.Exists('k')}")  # False

    # 3. Consultar valor (GetValue)
    print(f"Valor inicial de 'm': {ts.GetValue('m', 'valor')}")

    # 4. Modificar valor (ModifyAttr)
    ts.ModifyAttr("m", "valor", 5)
    print(f"Nuevo valor de 'm': {ts.GetValue('m', 'valor')}")

    # 5. Casos de error: duplicado, inexistente y atributo que no existe
    ts.Insert("m", {"tipo": "entero", "valor": 10})
    ts.ModifyAttr("k", "valor", 1)
    ts.GetValue("k", "valor")
    print(f"Atributo inexistente de 'm': {ts.GetValue('m', 'direccion')}")
