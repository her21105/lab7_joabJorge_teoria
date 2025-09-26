#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Versión con consola integrada para ejecutar directamente dentro de Anaconda o cualquier entorno
sin necesidad de abrir la terminal.

Uso:
    Ejecuta este archivo con doble clic o desde tu IDE.
    Se abrirá un menú donde puedes escribir los nombres de archivos de gramáticas
    separados por espacio, igual que harías en la consola:

    > g1.txt g2.txt

Después, el programa correrá el algoritmo de eliminación de ε-producciones sobre esos archivos.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Iterable

# Tipos básicos
NonTerminal = str
Symbol = str
Body = Tuple[Symbol, ...]
Grammar = Dict[NonTerminal, Set[Body]]

# Regex
ARROW = r"(?:→|->)"
BODY = r"(?:ε|[A-Za-z0-9]+)"
PROD_RE = re.compile(rf"^\s*([A-Z])\s*{ARROW}\s*{BODY}(?:\s*\|\s*{BODY})*\s*$")

def validate_line(line: str) -> Tuple[NonTerminal, List[str]]:
    m = PROD_RE.match(line)
    if not m:
        raise ValueError(f"Línea inválida: {line.strip()}")
    lhs = m.group(1)
    arrow_split = re.split(ARROW, line)
    rhs_raw = arrow_split[1]
    bodies = [part.strip() for part in rhs_raw.split('|')]
    return lhs, bodies

def parse_grammar(text: str) -> Grammar:
    grammar: Grammar = {}
    lines = [ln for ln in (ln.strip() for ln in text.splitlines()) if ln]
    for i, line in enumerate(lines, 1):
        lhs, bodies = validate_line(line)
        for body in bodies:
            if body == 'ε':
                prod: Body = tuple()
            else:
                for ch in body:
                    if not (ch.isalpha() or ch.isdigit()):
                        raise ValueError(f"Símbolo inválido '{ch}' en línea {i}: {line}")
                prod = tuple(body)
            grammar.setdefault(lhs, set()).add(prod)
    return grammar

def format_body(body: Body) -> str:
    return 'ε' if len(body) == 0 else ''.join(body)

def format_grammar(grammar: Grammar) -> str:
    lines = []
    for lhs in sorted(grammar.keys()):
        bodies = ' | '.join(sorted(format_body(b) for b in grammar[lhs]))
        lines.append(f"{lhs} → {bodies}")
    return '\n'.join(lines)

def find_nullable(grammar: Grammar) -> Set[NonTerminal]:
    nullable: Set[NonTerminal] = set()
    for A, prods in grammar.items():
        if tuple() in prods:
            nullable.add(A)
    changed = True
    while changed:
        changed = False
        for A, prods in grammar.items():
            if A in nullable:
                continue
            for body in prods:
                if all(sym.isupper() and sym in nullable for sym in body):
                    nullable.add(A)
                    changed = True
                    break
    return nullable

def power_set_indices(indices: List[int]) -> Iterable[List[int]]:
    n = len(indices)
    for mask in range(1, 1 << n):
        subset = [indices[i] for i in range(n) if (mask >> i) & 1]
        yield subset

def eliminate_epsilon(grammar: Grammar):
    log: List[str] = []
    log.append("Gramática original:\n" + format_grammar(grammar))
    nullable = find_nullable(grammar)
    log.append("Símbolos anulables: {" + ", ".join(sorted(nullable)) + "}")

    new_grammar: Grammar = {A: set() for A in grammar}
    for A, prods in grammar.items():
        for body in prods:
            if len(body) > 0:
                new_grammar[A].add(body)

    for A, prods in grammar.items():
        for body in prods:
            if len(body) == 0:
                continue
            nullable_pos = [i for i, sym in enumerate(body) if sym.isupper() and sym in nullable]
            if not nullable_pos:
                continue
            log.append(f"Expansión en {A} → {format_body(body)}; posiciones anulables: {nullable_pos}")
            seen_local: Set[Body] = set()
            for positions_to_remove in power_set_indices(nullable_pos):
                new_body = tuple(sym for i, sym in enumerate(body) if i not in positions_to_remove)
                if len(new_body) == 0:
                    continue
                if new_body not in seen_local:
                    seen_local.add(new_body)
                    new_grammar[A].add(new_body)
                    log.append(f"  + {A} → {format_body(new_body)} (eliminando {positions_to_remove})")

    new_grammar = {A: bodies for A, bodies in new_grammar.items() if bodies}
    log.append("Gramática final sin ε:\n" + format_grammar(new_grammar))
    return new_grammar, log, nullable

def load_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def main() -> None:
    print("============================================")
    print("Eliminación de producciones-ε de gramáticas")
    print("============================================")
    #print("Ingrese los nombres de archivos de gramática separados por espacios (ejemplo: g1.txt g2.txt):")
    #entrada = input("> ").strip()
    #if not entrada:
    #    print("No se ingresaron archivos.")
    #    return
    #archivos = entrada.split()

    archivos = [
        r"C:\Users\Joabh\Documents\GitHub\lab7_joabJorge_teoria\g1.txt",
        r"C:\Users\Joabh\Documents\GitHub\lab7_joabJorge_teoria\g2.txt",
        r"C:\Users\Joabh\Documents\GitHub\lab7_joabJorge_teoria\g2.txt"]
    for idx, path in enumerate(archivos, 1):
        print("=" * 80)
        print(f"Archivo {idx}: {path}")
        try:
            text = load_file(path)
            grammar = parse_grammar(text)
        except Exception as e:
            print(f"Error al procesar {path}: {e}")
            continue

        _, log, _ = eliminate_epsilon(grammar)
        for entry in log:
            print(entry)

if __name__ == '__main__':
    main()
