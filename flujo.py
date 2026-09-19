class Flujo:
    def __init__(self,ruta_fichero):
        with open(ruta_fichero, 'r', encoding='utf-8') as f:
            self.texto = f.read()
            #se abre el fichero y se guarda en la variable texto
        self.pos = 0
        #este puntero indica la posicion del caracter actual
        self.linea = 1
        self.columna = 0
        #contadores de linea y columna
        self.historial = []
        #esta sera la pila para recordar la posicion
    def newChar(self):
        if self.pos >= len(self.texto):
            return  ""
    #nos permite leer el siguiente caracter del flujo
    #guardamos la posicion actual
        self.historial.append((self.pos, self.linea, self.columna))
        caracter =self.texto[self.pos]
        self.pos += 1
        if caracter == "\n":
            self.linea += 1
            self.columna = 0
        else:
            self.columna += 1
        return caracter #caracter leido
        
    def returnChar(self):  #nos permitira devolver de nuevo al flujo el utlimo caracter que fue leido
        if self.historial:
            posicion, linea, columna = self.historial.pop()
            self.pos = posicion
            self.linea = linea
            self.columna = columna
        return self.texto[posicion]
    
    def getNumLinea(self): #nos devolvera el numero de linea del fichero que se esta leyendo
        return self.linea

    def getCharLinea(self): #nos indica que posicion ocupa el ultimo caracter leiod en la linea actual
    #estos ultimos dos metodos nos indicaran errores mas facilmente 
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


    
