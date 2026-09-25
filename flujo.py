class Flujo:
    def __init__(self, ruta_fichero):
        with open(ruta_fichero, "r", encoding="utf-8") as fichero:
            self.texto = fichero.read()

        self.pos = 0
        self.linea = 1
        self.columna = 0
        self.historial = []

    def newChar(self):
        """Lee un carácter y guarda el estado anterior para poder deshacerlo."""
        if self.pos >= len(self.texto):
            return None

        self.historial.append((self.pos, self.linea, self.columna))
        caracter = self.texto[self.pos]
        self.pos += 1

        if caracter == "\n":
            self.linea += 1
            self.columna = 0
        else:
            self.columna += 1

        return caracter

    def returnChar(self):
        """Deshace la última lectura y devuelve el carácter deshecho."""
        if not self.historial:
            return None

        posicion, linea, columna = self.historial.pop()
        caracter = self.texto[posicion]
        self.pos = posicion
        self.linea = linea
        self.columna = columna
        return caracter
    
    def getNumLinea(self):
        return self.linea

    def getCharLinea(self):
        return self.columna

"""if __name__ == "__main__":
    lector = Flujo("entrada.txt")
    print(f"Archivo cargado con exit, total de caracteres: {len(lector.texto)}")
    print(f"Posicion actual: Linea: {lector.linea}, Columna: {lector.columna}")
"""
if __name__ == "__main__":
    lector = Flujo("entrada.txt")

    print("Primer carácter:", repr(lector.newChar()))
    print("Segundo carácter:", repr(lector.newChar()))

    print("Línea actual:", lector.getNumLinea())
    print("Columna actual:", lector.getCharLinea())

    print("Carácter devuelto:", repr(lector.returnChar()))
    print("Leído otra vez:", repr(lector.newChar()))


    
