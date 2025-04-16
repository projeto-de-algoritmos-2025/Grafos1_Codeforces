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
    
    def ordenacao_topologica(self):
        grau_entrada = {materia: 0 for materia in self.grafo}
        for materia in self.grafo:
            for req in self.grafo[materia]:
                grau_entrada[req] += 1
        
        fila = deque([materia for materia in self.grafo if grau_entrada[materia] == 0])
        ordenacao = []

        while fila:
            materia = fila.popleft()
            ordenacao.append(materia)

            for vizinho in self.grafo[materia]:
                grau_entrada[vizinho] -= 1
                if grau_entrada[vizinho] == 0:
                    fila.append(vizinho)

        if len(ordenacao) != len(self.grafo):
            return None

        return ordenacao 
    
    def encontrar_cadeias(self):
        ordenacao = self.ordenacao_topologica()
        if not ordenacao:
            return []
        
        todas_cadeias = []

        def explorar_cadeias(materia, caminho_atual):
            caminho_atual.append(materia)

            if not self.grafo[materia]:
                if len(caminho_atual) > 1:
                    todas_cadeias.append(caminho_atual.copy())
                caminho_atual.pop()
                return
            
            for pre_requisito in self.grafo[materia]:
                    explorar_cadeias(pre_requisito, caminho_atual)

            caminho_atual.pop()

        nos_finais = [no for no in ordenacao if not any(no in self.grafo[outro] for outro in self.grafo)]
        for no_final in nos_finais:
            explorar_cadeias(no_final, [])

        cadeias_maximas = []
        todas_cadeias.sort(key=len, reverse=True)

        for cadeia in todas_cadeias:
            cadeia_set = set(cadeia)
            if not any(cadeia_set.issubset(set(c)) and len(cadeia) < len(c) for c in todas_cadeias):
                cadeias_maximas.append(cadeia[::-1])

        cadeias_finais = []
        for cadeia in cadeias_maximas:
            cadeia_set = set(cadeia)
            if not any(cadeia_set.issubset(set(c)) and len(cadeia) < len(c) for c in cadeias_maximas):
                cadeias_finais.append(cadeia)

        cadeias_finais.sort(key=lambda x: ordenacao.index(x[0]))
        return cadeias_finais