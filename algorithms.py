from collections import deque

class Grafo:
    def __init__(self, materias):
        self.grafo = {}
        self.semestres = {}
        self.nomes = {}
        
        for materia in materias:
            sigla = materia['sigla']
            self.grafo[sigla] = materia['pre_requisitos'] or []
            self.semestres[sigla] = materia['semestre_recomendado']
            self.nomes[sigla] = materia['nome']