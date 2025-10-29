# model.py
from dataclasses import dataclass, field
from typing import List, Union
from multimethod import multimeta
from rich.tree import Tree

# =====================================================================
# Clases Base para el Patrón Visitante y el AST
# =====================================================================

class Visitor(metaclass=multimeta):
    pass

@dataclass
class Node:
    lineno: int = field(kw_only=True, default=0)

    def accept(self, v: Visitor, *args, **kwargs):
        """ Puerta de entrada para el patrón Visitante. """
        return v.visit(self, *args, **kwargs)

    def pretty(self, arbol: Tree = None) -> Tree:
        """ Método para visualización del AST con formato personalizado. """
        if arbol is None:
            arbol = Tree(f"[AST] {self.__class__.__name__}")
        
        for clave, valor in self.__dict__.items():
            if clave == 'lineno': continue

            nodo_hijo = arbol.add(f"[ATRIBUTO] {clave}")
            if isinstance(valor, Node):
                valor.pretty(nodo_hijo)
            elif isinstance(valor, list):
                if valor:  # Solo mostrar si la lista no está vacía
                    nodo_lista = nodo_hijo.add(f"[LISTA] ({len(valor)} elementos)")
                    for i, elemento in enumerate(valor):
                        if isinstance(elemento, Node):
                            elemento.pretty(nodo_lista.add(f"[ELEMENTO {i+1}]"))
                        else:
                            nodo_lista.add(f"[{i+1}] = [cyan]{repr(elemento)}[/cyan]")
                else:
                    nodo_hijo.add("[dim][LISTA VACIA][/dim]")
            else:
                nodo_hijo.add(f"[yellow]{repr(valor)}[/yellow]")
        return arbol

@dataclass
class Statement(Node):
    pass

@dataclass
class Expression(Node):
    pass

@dataclass
class Type(Node):
    pass

# =====================================================================
# Nodos del Programa y Declaraciones (Completos para B-Minor)
# =====================================================================
@dataclass
class Program(Statement):
    body: List[Statement] = field(default_factory=list)

@dataclass
class Declaration(Statement):
    name: str
    type: Type

@dataclass
class VarDecl(Declaration):
    value: Expression = None

@dataclass
class ArrayDecl(Declaration):
    size: Expression = None
    value: List[Expression] = None

@dataclass
class Param(Node):
    name: str
    type: Type

@dataclass
class FuncDecl(Declaration):
    params: List[Param] = field(default_factory=list)
    body: Statement = None

# =====================================================================
# Nodos de Tipos
# =====================================================================
@dataclass
class SimpleType(Type):
    name: str

@dataclass
class ArrayType(Type):
    element_type: Type
    size: Expression = None

# =====================================================================
# Nodos de Sentencias
# =====================================================================
@dataclass
class IfStmt(Statement):
    condition: Expression
    true_body: Statement
    false_body: Statement = None

@dataclass
class ForStmt(Statement):
    init: Expression
    condition: Expression
    update: Expression
    body: Statement

@dataclass
class WhileStmt(Statement):
    condition: Expression
    body: Statement

@dataclass
class DoWhileStmt(Statement):
    body: Statement
    condition: Expression

@dataclass
class ReturnStmt(Statement):
    value: Expression = None

@dataclass
class PrintStmt(Statement):
    values: List[Expression] = field(default_factory=list)

@dataclass
class BlockStmt(Statement):
    statements: List[Statement] = field(default_factory=list)

# =====================================================================
# Nodos de Expresiones
# =====================================================================
@dataclass
class Assignment(Expression):
    location: Expression
    value: Expression

@dataclass
class BinOper(Expression):
    op: str
    left: Expression
    right: Expression

@dataclass
class UnaryOper(Expression):
    expr: Expression
    op: str

@dataclass
class PreInc(UnaryOper): op: str = '++'
@dataclass
class PreDec(UnaryOper): op: str = '--'
@dataclass
class PostInc(UnaryOper): op: str = '++'
@dataclass
class PostDec(UnaryOper): op: str = '--'

@dataclass
class Literal(Expression):
    value: Union[int, float, str, bool]

@dataclass
class Integer(Literal): pass
@dataclass
class Float(Literal): pass
@dataclass
class Boolean(Literal): pass
@dataclass
class Char(Literal): pass
@dataclass
class String(Literal): pass

@dataclass
class Location(Expression):
    pass

@dataclass
class VarLocation(Location):
    name: str

@dataclass
class ArraySubscript(Location):
    location: Location
    index: Expression

@dataclass
class FuncCall(Expression):
    name: str
    args: List[Expression] = field(default_factory=list)