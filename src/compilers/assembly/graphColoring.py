from assembly.common import *
import assembly.tac_ast as tac
import common.log as log
from common.prioQueue import PrioQueue

def chooseColor(x: tac.ident, forbidden: dict[tac.ident, set[int]]) -> int:
    """
    Returns the lowest possible color for variable x that is not forbidden for x.
    """
    ccolor = 0
    while ccolor in forbidden[x]:
        ccolor += 1
    return ccolor

def colorInterfGraph(g: InterfGraph, secondaryOrder: dict[tac.ident, int]={},
                     maxRegs: int=MAX_REGISTERS) -> RegisterMap:
    """
    Given an interference graph, computes a register map mapping a TAC variable
    to a TACspill variable. You have to implement the "simple graph coloring algorithm"
    from slide 58 here.

    - Parameter maxRegs is the maximum number of registers we are allowed to use.
    - Parameter secondaryOrder is used by the tests to get deterministic results even
      if two variables have the same number of forbidden colors.
    """
    log.debug(f"Coloring interference graph with maxRegs={maxRegs}")
    colors: dict[tac.ident, int] = {}
    # changed this to remove error
    forbidden: dict[tac.ident, set[int]] = {v: set() for v in g.vertices}
    q = PrioQueue(secondaryOrder)

    # SEE PAGE 58 OF SLIDES

    # Step 1: Initialize the priority queue with all vertices
    for v in g.vertices:
        q.push(v, 0)

    # Step 2-6: Color the graph
    while not q.isEmpty():
        u = q.pop()
        # Step 3: Find the lowest color not in forbidden[u]
        color = chooseColor(u, forbidden)
        
        # Step 4: Set the color for u
        colors[u] = color
        
        # Step 5: Update the forbidden sets of all adjacent vertices
        for v in g.succs(u):
            if v not in forbidden:
                continue
            # Update the forbidden sets of all adjacent vertices
            forbidden[v].add(color)
            q.incPrio(v)

    m = RegisterAllocMap(colors, maxRegs)
    return m
