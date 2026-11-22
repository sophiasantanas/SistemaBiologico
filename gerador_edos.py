from dataclasses import dataclass, field

@dataclass
class Termo:
    """"
    sign * rate * prod(factors) * f(pos, neg)
    """
    sinal: int                                         # +1 ou -1
    rate: str
    fatores: list[str] = field(default_factory=list)
    pos: list[str] = field(default_factory=list)
    neg: map[str][str] = field(default_factory=map)    # nome do inibidor -> constante de força de inibição

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


