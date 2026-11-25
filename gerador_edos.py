from dataclasses import dataclass, field
from grafo import Grafo, Aresta

@dataclass
class Termo:
    """
    sign * rate * prod(factors) * f(pos, neg)
    """
    sinal: int                                         # +1 ou -1
    rate: str
    fatores: list[str] = field(default_factory=list)
    pos: list[str] = field(default_factory=list)
    neg: dict[str, str] = field(default_factory=dict)    # nome do inibidor -> constante de força de inibição

@dataclass
class Equacao:
    variavel: str
    termos: list[Termo] = field(default_factory=list)

@dataclass
class SistemaEDO:
    variaveis: list[str]
    parametros: dict[str, float]                        # rates e constantes, constatens de força de ininbição e quaisquer outras constantes
    condicoes_iniciais: dict[str, float]                # valores iniciais de cada variável
    equacoes: list[Equacao] = field(default_factory=list)

def _neg_para_dict(aresta: Aresta) -> dict[str, str]:
    return {n: "K_" + n for n in aresta.neg}

def _gera_termo(aresta: Aresta) -> list[tuple[str, Termo]]:
    o, d = aresta.origem, aresta.destino
    pos = aresta.pos
    neg = _neg_para_dict(aresta)

    if o == d:
        if aresta.tipo == "+":
            return [(o, Termo(1, aresta.rate, [o], pos, neg))]
        if aresta.tipo == "-":
            return [(o, Termo(-1, aresta.rate, [o], pos, neg))]
        raise ValueError(f"laço com tipo inválido: {aresta.texto()}")
    match aresta.tipo:
        case "+":
            return [(d, Termo(1, aresta.rate, [o], pos, neg))]
        case "-":
            return [(d, Termo(-1, aresta.rate, [o,d], pos, neg))]
        case "-+":
            return [
                (o, Termo(-1, aresta.rate, [o], list(pos), dict(neg))),
                (d, Termo(1, aresta.rate, [o], list(pos), dict(neg))),
            ]
        case _:
            raise ValueError(f"tipo inválido: {aresta.texto()}")

def gera_sistema(grafo: Grafo, parametros: dict[str, float], condicoes_iniciais: dict[str, float]) -> SistemaEDO:
    equacoes = {v: Equacao(v) for v in grafo.vertices}

    for aresta in grafo.arestas:
        for variavel, termo in _gera_termo(aresta):
            equacoes[variavel].termos.append(termo)

    return SistemaEDO(
        variaveis=list(grafo.vertices),
        parametros=dict(parametros or {}),
        condicoes_iniciais=dict(condicoes_iniciais or {}),
        equacoes=[equacoes[v] for v in grafo.vertices],
    )

def _corpo(t: Termo) -> str:
    """rate*F1*F2*Pos... / (1 + K*n) ..."""
    texto = "*".join([t.rate] + list(t.fatores) + list(t.pos))
    for nome, k in t.neg.items():
        texto += f"/(1 + {k}*{nome})"
    return texto

def equacao_para_texto(eq: Equacao) -> str:
    if not eq.termos:
        return f"d{eq.variavel}/dt = 0"
    partes = []
    for i, t in enumerate(eq.termos):
        corpo = _corpo(t)
        if i == 0:
            partes.append(("-" if t.sinal < 0 else "") + corpo)
        else:
            partes.append(("- " if t.sinal < 0 else "+ ") + corpo)
    return f"d{eq.variavel}/dt = " + " ".join(partes)


def para_texto(sistema: SistemaEDO) -> str:
    return "\n".join(equacao_para_texto(eq) for eq in sistema.equacoes)