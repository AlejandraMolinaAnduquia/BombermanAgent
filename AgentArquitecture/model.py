import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import mesa
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from Controllers.fileLoad import FileLoad
from AgentArquitecture.agent import BomberManAgent
from mesa.datacollection import DataCollector

class BomberManModel(Model):
         
    def __init__(self, number_of_agents, width,height):
        self.number_agents = number_of_agents # Numero de agentes inicial
        self.grid=MultiGrid(width,height,True) #Parametro Falso para que no se salga de la grilla
        self.schedule=RandomActivation(self) # Planeador
        self.running=True
        self.matrizArchivo=self.leerArchivo()
        self.matriz, self.contadorId = self.crearMatrizAgentes(self.matrizArchivo)
        #self.ubicarAgentes(self.matriz)
        self.datacollector = mesa.DataCollector( #Agentes con y sin poder
            model_reporters = {
                "Wealthy Agents": self.current_wealthy_agents,
                "Non Wealthy Agents": self.current_non_wealthy_agents,
            }
        )
        
        for i in range(self.number_agents):
            newAgent = BomberManAgent(i, self)
            self.schedule.add(newAgent)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(newAgent, (x, y))

    def step(self) -> None:
        self.schedule.step()
        #Permite actualizar los datos cada paso
        self.datacollector.collect(self) #Llamar metodo para recolectra datos de cada iteración
        if BomberManModel.current_non_wealthy_agents(self)>20:
            self.running=False
        
    def current_wealthy_agents(model) -> int:
        return sum([1 for agent in model.schedule.agents if agent.wealth>0]) #Contar agentes con poder
        
    def current_non_wealthy_agents(model) -> int:
        return sum([1 for agent in model.schedule.agents if agent.wealth==0]) #Contar agentes sin poder
    
    def crearMatrizAgentes(self, matrizArchivo):
        # Inicializa el contador de ID
        contadorId = 0
        
        # Crea una matriz basada en el archivo proporcionado
        matriz = [[[] for _ in range(len(matrizArchivo[0]))] for _ in range(len(matrizArchivo))]

        # Devuelve exactamente dos valores: la matriz y el contadorId
        return matriz, contadorId

       
    def leerArchivo(self):
        fileLoad = FileLoad()
        # Ruta absoluta basada en la ubicación de este archivo (model.py)
        base_dir = os.path.dirname(__file__)  # Obtiene la ruta de la carpeta de model.py
        ruta_mapa = os.path.join(base_dir, "../Data/Maps/mapa1.txt")  # Crea la ruta absoluta

        # Normaliza la ruta para que funcione en cualquier sistema operativo
        ruta_mapa = os.path.normpath(ruta_mapa)
        matrizArchivo = fileLoad.cargar_matriz_archivo(ruta_mapa)
        return matrizArchivo
        
    def get_valid_nodes(self):
            nodos_validos = []
            filas = len(self.matrizArchivo)
            columnas = len(self.matrizArchivo[0])
            self.matrizArchivo.reverse()
            for i in range(filas):
                for j in range(columnas):
                    if self.matrizArchivo[i][j] == "C" or self.matrizArchivo[i][j] == "C_g" or self.matrizArchivo[i][j] == "C_b":  # Define tu propio criterio aquí
                        nodos_validos.append((j, i))

            return nodos_validos

    """
    Recibe una matriz de agentes y los ubica en la grilla.
    Cómo mesa ubica las posiciones cómo en el plano cartesiano, se debe recorrer la matriz 
    de forma inversa
    """
    def ubicarAgentes(self, matriz):
        contadorX=0
        contadorY=len(matriz)-1
        for i in range(len(matriz)):
            #Reinicia el contador de X cuando cambia de fila y disminuye el contador de Y 
            #para que se ubique en la fila de abajo
            if (contadorX!=0):
                contadorY-=1
                contadorX=0     

            for j in range(len(matriz[i])):

                self.schedule.add(matriz[i][j][0])
                self.grid.place_agent(matriz[i][j][0], (contadorX, contadorY))
                contadorX+=1
                print("contador X:  "+ str(contadorX) +" contador Y "+ str(contadorY) +" "+ str(matriz[i][j][0]))


    def nextId(self):
        self.contadorId+=1
        return self.contadorId
    