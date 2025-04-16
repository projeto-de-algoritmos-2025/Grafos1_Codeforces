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


    def bfs_recomendacao(self, cursadas, semestre_atual, max_por_semestre=5):
        recomendacoes = {}
        semestre = semestre_atual
        concluidas = set(cursadas)

        while True: 
            disponiveis = [
                materia for materia in self.grafo
                if materia not in concluidas and 
                all(req in concluidas for req in self.grafo[materia])
            ]

            if not disponiveis:
                break 

            disponiveis.sort(key=lambda x: self.semestres[x])
            recomendacoes_semestre = disponiveis[:max_por_semestre]
            recomendacoes[f"Semestre {semestre}"] = recomendacoes_semestre
            concluidas.update(recomendacoes_semestre)
            semestre += 1 
        return recomendacoes