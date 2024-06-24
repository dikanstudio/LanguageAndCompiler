from assembly.common import *
from assembly.graph import Graph
import assembly.tac_ast as tac

def instrDef(instr: tac.instr) -> set[tac.ident]:
    """
    Returns the set of identifiers defined by some instrucution.
    """
    match instr:
        case tac.Assign(var=var, left=_):
            return {var}
        case tac.Call(var=var, name=_, args=_):
            return {var} if var is not None else set()
        case tac.GotoIf(test=_, label=_):
            return set()
        case tac.Goto(label=_):
            return set()
        case tac.Label(label=_):
            return set()
        
def usePrim(prim: tac.prim) -> set[tac.ident]:
    """
    Returns the set of identifiers used by a primitive.
    """
    match prim:
        case tac.Const(value=_):
            return set()
        case tac.Name(var=var):
            return {var}

def instrUse(instr: tac.instr) -> set[tac.ident]:
    """
    Returns the set of identifiers used by some instrucution.
    """
    match instr:
        case tac.Assign(var=_, left=exp):
            match exp:
                case tac.Prim(p=prim):
                    return usePrim(prim)
                case tac.BinOp(left=left, right=right, op=_):
                    return usePrim(left) | usePrim(right)
        case tac.Call(var=_, name=_, args=args):
            # We have to consider the case where args is a list of Name
            return {arg.var for arg in args if isinstance(arg, tac.Name)}
        case tac.GotoIf(test=prim, label=_):
            return usePrim(prim)
        case tac.Goto(label=_):
            return set()
        case tac.Label(label=_):
            return set()


# Each individual instruction has an identifier. This identifier is the tuple
# (index of basic block, index of instruction inside the basic block)
type InstrId = tuple[int, int]

class InterfGraphBuilder:
    def __init__(self):
        # self.before holds, for each instruction I, to set of variables live before I.
        self.before: dict[InstrId, set[tac.ident]] = {}
        # self.after holds, for each instruction I, to set of variables live after I.
        self.after: dict[InstrId, set[tac.ident]] = {}

    def __liveStart(self, bb: BasicBlock, s: set[tac.ident]) -> set[tac.ident]:
        """
        Given a set of variables s and a basic block bb, __liveStart computes
        the set of variables live at the beginning of bb, assuming that s
        are the variables live at the end of the block.

        Essentially, you have to implement the subalgorithm "Computing L_start" from
        slide 46 here. You should update self.after and self.before while traversing
        the instructions of the basic block in reverse.
        """
        # Get the instructions of the basic block
        instructions = bb.instrs
        n = len(instructions)
        
        # Initialize L_after(n) = S
        live_after = s

        # Iterate over the instructions in reverse order
        for k in range(n - 1, -1, -1):
            # Get the instruction ID
            instr_id = (bb.index, k)
            # Get the instruction at index k
            instr = instructions[k]

            # L_before(k) = (L_after(k) \ def(instr)) ∪ use(instr)
            live_before = (live_after - instrDef(instr)) | instrUse(instr)
            
            # Update self.before and self.after
            self.after[instr_id] = live_after
            self.before[instr_id] = live_before
            
            # Set live_after for the next iteration
            live_after = live_before

        # Return L_before(0) as L_start(B, S)
        #return live_after
        return self.before.get((bb.index, 0), set())

    def __liveness(self, g: ControlFlowGraph):
        """
        This method computes liveness information and fills the sets self.before and
        self.after.

        You have to implement the algorithm for computing liveness in a CFG from
        slide 46 here.
        """
        # Initialize IN and OUT sets for each block
        in_sets: dict[int, set[tac.ident]] = {block: set() for block in g.vertices}
        out_sets: dict[int, set[tac.ident]] = {block: set() for block in g.vertices}
        
        # Flag to check if any changes were made in an iteration
        changed = True

        while changed:
            changed = False

            # Process each block in reverse order of their index
            for block_index in sorted(g.vertices, reverse=True):
                block = g.getData(block_index)
                
                # Compute OUT[B] as the union of IN sets of successors
                new_out_set: set[tac.ident] = set()
                for succ in g.succs(block_index):
                    new_out_set |= in_sets[succ]

                # if OUT set changed
                if new_out_set != out_sets[block_index]:
                    out_sets[block_index] = new_out_set
                    changed = True

                # Compute IN[B] using OUT[B] and liveStart
                new_in_set = self.__liveStart(block, out_sets[block_index])
                if new_in_set != in_sets[block_index]:
                    in_sets[block_index] = new_in_set
                    changed = True

        # Update self.before and self.after using the final IN and OUT sets
        for block_index in g.vertices:
            # Get the block and its instructions
            block = g.getData(block_index)
            # Get the instructions of the block
            instructions = block.instrs
            
            # Initialize live_after with the OUT set of the block
            live_after = out_sets[block_index]
            # Iterate over the instructions in reverse order
            for i in range(len(instructions) - 1, -1, -1):
                # Get the instruction ID
                instr_id = (block.index, i)
                # Update self.before and self.after
                self.after[instr_id] = live_after
                self.before[instr_id] = (live_after - instrDef(instructions[i])) | instrUse(instructions[i])
                live_after = self.before[instr_id]

        #print("IN sets:", in_sets)
        #print("OUT sets:", out_sets)
        #print("AHHHHHH")


    def __addEdgesForInstr(self, instrId: InstrId, instr: tac.instr, interfG: InterfGraph):
        """
        Given an instruction and its ID, adds the edges resulting from the instruction
        to the interference graph.

        You should implement the algorithm specified on the slide
        "Computing the interference graph" (slide 50) here.
        """
        # Get the set of variables live before and after the instruction
        live_before = self.before[instrId]
        live_after = self.after[instrId]

        all_vars = live_before | live_after
        def_vars = instrDef(instr)

        print(f"Instruction ID: {instrId}, Instruction: {instr}")
        print(f"Live before: {live_before}, Live after: {live_after}")
        print(f"Def vars: {def_vars}")

        for v in def_vars:
            if v not in interfG.vertices:
                interfG.addVertex(v, None)
        
        for u in all_vars:
            if u not in interfG.vertices:
                interfG.addVertex(u, None)
            for v in def_vars:
                if u != v:
                    # Ensure we're not adding an edge if it's not a real interference
                    if not (isinstance(instr, tac.Assign) and isinstance(instr.left, tac.BinOp) and 
                            isinstance(instr.left.left, tac.Name) and u == instr.left.left.var):
                        print(f"Adding edge between {u} and {v}")
                        interfG.addEdge(u, v)

    def build(self, g: ControlFlowGraph) -> InterfGraph:
        """
        This method builds the interference graph. It performs three steps:

        - Use __liveness to fill the sets self.before and self.after.
        - Setup the interference graph as an undirected graph containing all variables
        defined or used by any instruction of any basic block. Initially, the
        graph does not have any edges.
        - Use __addEdgesForInstr to fill the edges of the interference graph.
        """
        # Use __liveness to fill the sets self.before and self.after
        self.__liveness(g)

        # Setup the interference graph
        interfG = Graph[tac.ident, None](kind='undirected')
        all_vars: set[tac.ident] = set()

        for block_index in g.vertices:
            block = g.getData(block_index)
            for i, instr in enumerate(block.instrs):
                all_vars |= instrDef(instr) | instrUse(instr)

        for var in all_vars:
            interfG.addVertex(var, None)

        for block_index in g.vertices:
            block = g.getData(block_index)
            for i, instr in enumerate(block.instrs):
                instr_id = (block.index, i)
                self.__addEdgesForInstr(instr_id, instr, interfG)

        return interfG


def buildInterfGraph(g: ControlFlowGraph) -> InterfGraph:
    builder = InterfGraphBuilder()
    return builder.build(g)
