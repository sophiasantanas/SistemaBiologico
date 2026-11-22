#  cada vertice é uma população (S, P, R)
#  cada aresta é uma interação de uma população em outra
#
#  compoem a aresta
#    origem: de onde sai          (ex: "S")
#    destino: para onde vai       (ex: "P")
#    tipo: "+", "-" ou "-+"
#    rate: nome da taxa           (ex: "k_diff")
#    pos: lista de quem ajuda     (ex: ["R"])
#    neg: lista de quem atrapalha
#
#  interações
#    A  + -> B   positiva       (tipo "+",  A diferente de B)
#    A  - -> B   negativa       (tipo "-",  A diferente de B)
#    A -+ -> B   diferenciação  (tipo "-+", A vira B)
#    A  + -> A   auto-estímulo  (tipo "+",  laço)
#    A  - -> A   morte          (tipo "-",  laço)

import json


class Aresta:
    def __init__(self, origem, destino, tipo, rate, pos, neg):
        self.origem = origem
        self.destino = destino
        self.tipo = tipo
        self.rate = rate
        self.pos = pos
        self.neg = neg

    def laco(self):
        return self.origem == self.destino

    def nome_do_tipo(self):
        if self.laco():
            if self.tipo == "+":
                return "auto-estimulo"
            return "morte"
        if self.tipo == "+":
            return "positiva"
        if self.tipo == "-":
            return "negativa"
        return "diferenciacao"

    def sinal(self):
        if self.tipo == "-":
            return -1
        return 1

    def texto(self):
        return self.origem + " " + self.tipo + "-> " + self.destino + "  [" + self.rate + "]  (" + self.nome_do_tipo() + ")"


class Grafo:
    def __init__(self):
        self.vertices = []
        self.arestas = []

    # montagem
    def adicionar_vertice(self, nome):
        self.vertices.append(nome)

    def adicionar_aresta(self, origem, destino, tipo, rate, pos, neg):
        self.arestas.append(Aresta(origem, destino, tipo, rate, pos, neg))

    def carregar_json(self, caminho):
        arquivo = open(caminho)
        dados = json.load(arquivo)
        arquivo.close()

        for v in dados["vertices"]:
            self.adicionar_vertice(v)

        for a in dados["arestas"]:
            self.adicionar_aresta(a["origem"], a["destino"], a["tipo"], a["rate"], a["pos"], a["neg"])

    # consultas
    def arestas_saindo(self, v):
        resultado = []
        for a in self.arestas:
            if a.origem == v:
                resultado.append(a)
        return resultado

    def arestas_chegando(self, v):
        resultado = []
        for a in self.arestas:
            if a.destino == v:
                resultado.append(a)
        return resultado

    def vizinhos(self, v):
        resultado = []
        for a in self.arestas_saindo(v):
            if not a.laco() and a.destino not in resultado:
                resultado.append(a.destino)
        return resultado

    def flag_auto_estimulo(self, v):
        for a in self.arestas_saindo(v):
            if a.laco() and a.tipo == "+":
                return True
        return False

    def flag_morte(self, v):
        for a in self.arestas_saindo(v):
            if a.laco() and a.tipo == "-":
                return True
        return False

    # caminhos e ciclos
    def caminhos(self, inicio, fim):
        encontrados = []
        self.explorar(inicio, fim, [inicio], [], encontrados)
        return encontrados

    def explorar(self, atual, fim, visitados, caminho, encontrados):
        for a in self.arestas_saindo(atual):
            if a.destino == fim:
                encontrados.append(caminho + [a])
            elif a.destino not in visitados:
                self.explorar(a.destino, fim, visitados + [a.destino], caminho + [a], encontrados)

    def ciclos(self):
        # o mesmo ciclo aparece uma vez para cada vértice dele;
        todos = []
        for v in self.vertices:
            for ciclo in self.caminhos(v, v):
                primeiro = True
                for a in ciclo:
                    if self.vertices.index(a.destino) < self.vertices.index(v):
                        primeiro = False
                if primeiro:
                    todos.append(ciclo)
        return todos

    def sinal_caminho(self, caminho):
        #de acordo com o xandao, o sinal obedece a ultima
        ultima = caminho[-1]
        if ultima.sinal() > 0:
            return "+"
        return "-"

    def caminho_texto(self, caminho):
        texto = caminho[0].origem
        for a in caminho:
            texto = texto + " " + a.tipo + "-> " + a.destino
        return texto

    # nocaute
    def nocaute(self, x):
        novo = Grafo()

        for v in self.vertices:
            if v != x:
                novo.adicionar_vertice(v)

        for a in self.arestas:
            if a.origem != x and a.destino != x and x not in a.pos:
                neg = []
                for n in a.neg:
                    if n != x:
                        neg.append(n)
                novo.adicionar_aresta(a.origem, a.destino, a.tipo, a.rate, a.pos, neg)

        return novo

    def mostrar(self):
        print("Vértices:", self.vertices)
        print("Arestas:")
        for a in self.arestas:
            print("  ", a.texto())


# main
def titulo(nome):
    print()
    print("-" * 40)
    print(" " + nome)
    print("-" * 40)


def main():
    g = Grafo()
    g.carregar_json("ex3.json")

    titulo("GRAFO")
    g.mostrar()

    titulo("VÉRTICES")
    for v in g.vertices:
        print("  " + v)
        print("     vai para:      ", g.vizinhos(v))
        print("     auto-estímulo: ", g.flag_auto_estimulo(v))
        print("     morte:         ", g.flag_morte(v))

    titulo("CICLOS")
    for c in g.ciclos():
        print("  ", g.caminho_texto(c), "   sinal:", g.sinal_caminho(c))

    titulo("CAMINHOS DE S ATÉ R")
    for c in g.caminhos("S", "R"):
        print("  ", g.caminho_texto(c), "   sinal:", g.sinal_caminho(c))

    for x in g.vertices:
        titulo("NOCAUTE DE " + x)
        g.nocaute(x).mostrar()


if __name__ == "__main__":
    main()
