class TablaSimbolos:
    # valor, tipo, direccion de memoria
    # el nombre sera la clave del diccionario

    # diccionario vacio
    def __init__(self):
        self.tabla = {}

    def Exists(self, id):
        return id in self.tabla

    def InsertSymbol(self, id, atributos=None):
        if atributos is None:
            atributos = {}
        if self.Exists(id):
            print(f"El símbolo '{id}' ya existe en la tabla.")
            return False
        self.tabla[id] = atributos
        return True

    def ModifySymbol(self, id, atributo, new_value):
        if not self.Exists(id):
            print(f"El símbolo '{id}' no existe en la tabla.")
            return False
        self.tabla[id][atributo] = new_value
        return True

    def GetValue(self, id, atributo):
        if not self.Exists(id):
            print(f"El símbolo '{id}' no existe en la tabla.")
            return None
        return self.tabla[id].get(atributo, None)

    def __str__(self):
        return str(self.tabla)

# Alias para compatibilidad
Simbolos = TablaSimbolos

#diccionario que contendra los simbolos, la clave sera el nombre del simbolo y el valor sera un objeto de la clase Simbolos
if __name__ == "__main__":
    ts = Simbolos()

    # 1. Insertar variables con sus atributos iniciales
    ts.InsertSymbol("contador", {"tipo": "entero", "valor": 0})
    ts.InsertSymbol("precio", {"tipo": "real", "valor": 19.99})

    # 2. Comprobar existencia (Exists)
    print(f"¿Existe 'contador'?: {ts.Exists('contador')}")  # True
    print(f"¿Existe 'total'?: {ts.Exists('total')}")        # False

    # 3. Consultar valor (GetValue)
    print(f"Valor inicial de 'contador': {ts.GetValue('contador', 'valor')}")

    # 4. Modificar valor (ModifySymbol)
    ts.ModifySymbol("contador", "valor", 5)
    print(f"Nuevo valor de 'contador': {ts.GetValue('contador', 'valor')}")

    # 5. Intentar insertar un duplicado
    ts.InsertSymbol("contador", {"tipo": "entero", "valor": 10})
    