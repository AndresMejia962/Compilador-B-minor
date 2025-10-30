# parser.py
import logging
import sly
from rich import print

from bminor_lexer import Lexer
from errors import error, errors_detected
from model import *

def asignar_linea(nodo, numero_linea):
    if nodo:
        nodo.lineno = numero_linea
    return nodo

class AnalizadorSintactico(sly.Parser):
    log = logging.getLogger()
    log.setLevel(logging.ERROR)
    debugfile = 'parser.log'

    tokens = Lexer.tokens

    @_("lista_declaraciones")
    def programa(self, p):
        return Program(p.lista_declaraciones)

    @_("declaracion lista_declaraciones")
    def lista_declaraciones(self, p):
        return [p.declaracion] + p.lista_declaraciones if p.declaracion else p.lista_declaraciones
    @_("empty")
    def lista_declaraciones(self, p):
        return []

    # Declaraciones
    @_("ID ':' tipo_simple ';'")
    def declaracion(self, p):
        return asignar_linea(VarDecl(p.ID, p.tipo_simple), p.lineno)
    @_("ID ':' tipo_array_con_tamano ';'")
    def declaracion(self, p):
        return asignar_linea(ArrayDecl(p.ID, p.tipo_array_con_tamano), p.lineno)

    # Permitir declaración de array sin tamaño
    @_("ID ':' tipo_array ';'")
    def declaracion(self, p):
        return asignar_linea(ArrayDecl(p.ID, p.tipo_array), p.lineno)

    @_("ID ':' tipo_funcion ';'")
    def declaracion(self, p):
        declaracion_funcion = p.tipo_funcion
        declaracion_funcion.name = p.ID
        return asignar_linea(declaracion_funcion, p.lineno)

    @_("declaracion_inicializada")
    def declaracion(self, p):
        return p.declaracion_inicializada
    
    # Declaraciones con Inicialización
    @_("ID ':' tipo_simple '=' expr ';'")
    def declaracion_inicializada(self, p):
        return asignar_linea(VarDecl(p.ID, p.tipo_simple, p.expr), p.lineno)
    @_("ID ':' tipo_array_con_tamano '=' '{' lista_expresiones_opcional '}' ';'")
    def declaracion_inicializada(self, p):
        return asignar_linea(ArrayDecl(p.ID, p.tipo_array_con_tamano, value=p.lista_expresiones_opcional), p.lineno)

    # Permitir inicialización de array sin tamaño
    @_("ID ':' tipo_array '=' '{' lista_expresiones_opcional '}' ';'")
    def declaracion_inicializada(self, p):
        return asignar_linea(ArrayDecl(p.ID, p.tipo_array, value=p.lista_expresiones_opcional), p.lineno)

    # Variantes sin punto y coma (para cabecera de FOR)
    @_("ID ':' tipo_simple")
    def declaracion_sin_pyc(self, p):
        return asignar_linea(VarDecl(p.ID, p.tipo_simple), p.lineno)
    @_("ID ':' tipo_array_con_tamano")
    def declaracion_sin_pyc(self, p):
        return asignar_linea(ArrayDecl(p.ID, p.tipo_array_con_tamano), p.lineno)
    @_("ID ':' tipo_array")
    def declaracion_sin_pyc(self, p):
        return asignar_linea(ArrayDecl(p.ID, p.tipo_array), p.lineno)

    @_("ID ':' tipo_simple '=' expr")
    def declaracion_inicializada_sin_pyc(self, p):
        return asignar_linea(VarDecl(p.ID, p.tipo_simple, p.expr), p.lineno)
    @_("ID ':' tipo_array_con_tamano '=' '{' lista_expresiones_opcional '}'")
    def declaracion_inicializada_sin_pyc(self, p):
        return asignar_linea(ArrayDecl(p.ID, p.tipo_array_con_tamano, value=p.lista_expresiones_opcional), p.lineno)
    @_("ID ':' tipo_array '=' '{' lista_expresiones_opcional '}'")
    def declaracion_inicializada_sin_pyc(self, p):
        return asignar_linea(ArrayDecl(p.ID, p.tipo_array, value=p.lista_expresiones_opcional), p.lineno)

    @_("ID ':' tipo_funcion '=' '{' lista_sentencias_opcional '}'")
    def declaracion_inicializada(self, p):
        declaracion_funcion = p.tipo_funcion
        declaracion_funcion.name = p.ID
        declaracion_funcion.body = asignar_linea(BlockStmt(p.lista_sentencias_opcional), p.lineno)
        return asignar_linea(declaracion_funcion, p.lineno)

    # Sentencias
    @_("lista_sentencias")
    def lista_sentencias_opcional(self, p):
        return p.lista_sentencias
    @_("empty")
    def lista_sentencias_opcional(self, p):
        return []

    @_("sentencia lista_sentencias")
    def lista_sentencias(self, p):
        return [p.sentencia] + p.lista_sentencias
    @_("sentencia")
    def lista_sentencias(self, p):
        return [p.sentencia]

    @_("sentencia_abierta", "sentencia_cerrada")
    def sentencia(self, p):
        return p[0]
    @_("WHILE '(' expr ')' sentencia")
    def sentencia(self, p):
        return asignar_linea(WhileStmt(p.expr, p.sentencia), p.lineno)
    @_("DO sentencia WHILE '(' expr ')' ';'")
    def sentencia(self, p):
        return asignar_linea(DoWhileStmt(p.sentencia, p.expr), p.lineno)

    @_("sentencia_if_cerrada", "sentencia_for_cerrada", "sentencia_simple")
    def sentencia_cerrada(self, p):
        return p[0]
    @_("sentencia_if_abierta", "sentencia_for_abierta")
    def sentencia_abierta(self, p):
        return p[0]

    @_("IF '(' expr ')' sentencia_cerrada ELSE sentencia_cerrada")
    def sentencia_if_cerrada(self, p):
        return asignar_linea(IfStmt(p.expr, p.sentencia_cerrada0, p.sentencia_cerrada1), p.lineno)
    @_("IF '(' expr ')' sentencia")
    def sentencia_if_abierta(self, p):
        return asignar_linea(IfStmt(p.expr, p.sentencia), p.lineno)
    @_("IF '(' expr ')' sentencia_cerrada ELSE sentencia_abierta")
    def sentencia_if_abierta(self, p):
        return asignar_linea(IfStmt(p.expr, p.sentencia_cerrada, p.sentencia_abierta), p.lineno)

    @_("FOR '(' for_init ';' expr_opcional ';' expr_opcional ')' sentencia_abierta")
    def sentencia_for_abierta(self, p):
        return asignar_linea(ForStmt(p.for_init, p.expr_opcional0, p.expr_opcional1, p.sentencia_abierta), p.lineno)
    @_("FOR '(' for_init ';' expr_opcional ';' expr_opcional ')' sentencia_cerrada")
    def sentencia_for_cerrada(self, p):
        return asignar_linea(ForStmt(p.for_init, p.expr_opcional0, p.expr_opcional1, p.sentencia_cerrada), p.lineno)

    @_("sentencia_print", "sentencia_return", "sentencia_bloque", "declaracion", "expr ';'")
    def sentencia_simple(self, p):
        return p[0]
    @_("PRINT lista_expresiones ';'")
    def sentencia_print(self, p):
        return asignar_linea(PrintStmt(p.lista_expresiones), p.lineno)
    @_("RETURN expr ';'")
    def sentencia_return(self, p):
        return asignar_linea(ReturnStmt(p.expr), p.lineno)
    @_("RETURN ';'")
    def sentencia_return(self, p):
        return asignar_linea(ReturnStmt(), p.lineno)
    @_("'{' lista_sentencias_opcional '}'")
    def sentencia_bloque(self, p):
        return asignar_linea(BlockStmt(p.lista_sentencias_opcional), p.lineno)

    # Expresiones (Reglas de precedencia)
    @_("expr1")
    def expr(self, p): return p.expr1
    @_("ubicacion '=' expr1")
    def expr1(self, p): return asignar_linea(Assignment(p.ubicacion, p.expr1), p.lineno)
    @_("expr2")
    def expr1(self, p): return p.expr2
    @_("expr2 LOR expr3")
    def expr2(self, p): return asignar_linea(BinOper('||', p.expr2, p.expr3), p.lineno)
    @_("expr3")
    def expr2(self, p): return p.expr3
    @_("expr3 LAND expr4")
    def expr3(self, p): return asignar_linea(BinOper('&&', p.expr3, p.expr4), p.lineno)
    @_("expr4")
    def expr3(self, p): return p.expr4
    @_("expr4 EQ expr5", "expr4 NE expr5", "expr4 LT expr5", "expr4 LE expr5", "expr4 GT expr5", "expr4 GE expr5")
    def expr4(self, p): return asignar_linea(BinOper(p[1], p.expr4, p.expr5), p.lineno)
    @_("expr5")
    def expr4(self, p): return p.expr5
    @_("expr5 '+' expr6", "expr5 '-' expr6")
    def expr5(self, p): return asignar_linea(BinOper(p[1], p.expr5, p.expr6), p.lineno)
    @_("expr6")
    def expr5(self, p): return p.expr6
    @_("expr6 '*' expr7", "expr6 '/' expr7", "expr6 '%' expr7")
    def expr6(self, p): return asignar_linea(BinOper(p[1], p.expr6, p.expr7), p.lineno)
    @_("expr7")
    def expr6(self, p): return p.expr7
    @_("expr7 '^' expr8")
    def expr7(self, p): return asignar_linea(BinOper('^', p.expr7, p.expr8), p.lineno)
    @_("expr8")
    def expr7(self, p): return p.expr8
    
    # Expresiones Unarias y de Incremento/Decremento
    @_("'-' expr8", "'!' expr8")
    def expr8(self, p): return asignar_linea(UnaryOper(p.expr8, p[0]), p.lineno)
    @_("INC expr9")
    def expr8(self, p): return asignar_linea(PreInc(expr=p.expr9), p.lineno)
    @_("DEC expr9")
    def expr8(self, p): return asignar_linea(PreDec(expr=p.expr9), p.lineno)
    @_("expr9")
    def expr8(self, p): return p.expr9
    @_("expr9 INC")
    def expr9(self, p): return asignar_linea(PostInc(expr=p.expr9), p.lineno)
    @_("expr9 DEC")
    def expr9(self, p): return asignar_linea(PostDec(expr=p.expr9), p.lineno)
    @_("grupo")
    def expr9(self, p): return p.grupo

    # Expresiones Agrupadas y Factores
    @_("'(' expr ')'")
    def grupo(self, p): return p.expr
    @_("ID '(' lista_expresiones_opcional ')'")
    def grupo(self, p): return asignar_linea(FuncCall(p.ID, p.lista_expresiones_opcional), p.lineno)
    @_("ubicacion")
    def grupo(self, p): return p.ubicacion
    @_("factor")
    def grupo(self, p): return p.factor

    @_("ID")
    def ubicacion(self, p): return asignar_linea(VarLocation(p.ID), p.lineno)
    @_("ubicacion '[' expr ']'")
    def ubicacion(self, p): return asignar_linea(ArraySubscript(p.ubicacion, p.expr), p.lineno)

    @_("INTEGER_LITERAL")
    def factor(self, p): return asignar_linea(Integer(p[0]), p.lineno)
    @_("FLOAT_LITERAL")
    def factor(self, p): return asignar_linea(Float(p[0]), p.lineno)
    @_("CHAR_LITERAL")
    def factor(self, p): return asignar_linea(Char(p[0]), p.lineno)
    @_("STRING_LITERAL")
    def factor(self, p): return asignar_linea(String(p[0]), p.lineno)
    @_("TRUE")
    def factor(self, p): return asignar_linea(Boolean(True), p.lineno)
    @_("FALSE")
    def factor(self, p): return asignar_linea(Boolean(False), p.lineno)

    # Listas
    @_("lista_expresiones")
    def lista_expresiones_opcional(self, p): return p.lista_expresiones
    @_("empty")
    def lista_expresiones_opcional(self, p): return []
    @_("expr ',' lista_expresiones")
    def lista_expresiones(self, p): return [p.expr] + p.lista_expresiones
    @_("expr")
    def lista_expresiones(self, p): return [p.expr]

    @_("lista_parametros")
    def lista_parametros_opcional(self, p): return p.lista_parametros
    @_("empty")
    def lista_parametros_opcional(self, p): return []
    @_("lista_parametros ',' parametro")
    def lista_parametros(self, p): return p.lista_parametros + [p.parametro]
    @_("parametro")
    def lista_parametros(self, p): return [p.parametro]
    @_("ID ':' tipo_simple")
    def parametro(self, p): return asignar_linea(Param(p.ID, p.tipo_simple), p.lineno)
    @_("ID ':' tipo_array")
    def parametro(self, p): return asignar_linea(Param(p.ID, p.tipo_array), p.lineno)
    @_("ID ':' tipo_array_con_tamano")
    def parametro(self, p): return asignar_linea(Param(p.ID, p.tipo_array_con_tamano), p.lineno)

    # Tipos
    @_("INTEGER", "FLOAT", "BOOLEAN", "CHAR", "STRING", "VOID")
    def tipo_simple(self, p): 
        return asignar_linea(SimpleType(p[0]), p.lineno)
    
    @_("ARRAY '[' ']' tipo_simple")
    def tipo_array(self, p): 
        return asignar_linea(ArrayType(p.tipo_simple), p.lineno)
    
    @_("ARRAY '[' expr ']' tipo_simple")
    def tipo_array_con_tamano(self, p): 
        return asignar_linea(ArrayType(p.tipo_simple, p.expr), p.lineno)
    
    # Regla nueva: Arrays anidados con tamaño
    @_("ARRAY '[' expr ']' tipo_array_con_tamano")
    def tipo_array_con_tamano(self, p):
        return asignar_linea(ArrayType(p.tipo_array_con_tamano, p.expr), p.lineno)
    
    @_("FUNCTION tipo_simple '(' lista_parametros_opcional ')'")
    def tipo_funcion(self, p):
        return FuncDecl(name=None, type=p.tipo_simple, params=p.lista_parametros_opcional)

    @_("empty")
    def expr_opcional(self, p): return None
    @_("expr")
    def expr_opcional(self, p): return p.expr

    # Sección init específica de FOR (permite declaración y expr)
    @_("empty")
    def for_init(self, p): return None
    @_("expr")
    def for_init(self, p): return p.expr
    @_("declaracion_inicializada_sin_pyc")
    def for_init(self, p): return p.declaracion_inicializada_sin_pyc
    @_("declaracion_sin_pyc")
    def for_init(self, p): return p.declaracion_sin_pyc
    @_("")
    def empty(self, p): pass

    # Manejador de errores requerido por SLY
    def error(self, token):
        if token:
            error(f"Error de sintaxis en '{token.value}'", token.lineno)
        else:
            error("Error de sintaxis al final del archivo (EOF)")

def analizar_sintaxis(texto):
    lexer = Lexer()
    parser = AnalizadorSintactico()
    return parser.parse(lexer.tokenize(texto))

# Compatibilidad con pruebas existentes
# Exporta nombres esperados: Parser y parse
Parser = AnalizadorSintactico

def parse(texto: str):
    return analizar_sintaxis(texto)