// Read-only: print linear instructions from the program entry and list functions by address.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;

public class AgiEntry extends GhidraScript {
    private static final int LIMIT = 70;

    @Override
    public void run() {
        Address entry = currentProgram.getSymbolTable().getExternalEntryPointIterator().next();
        Instruction current = getInstructionAt(entry);
        for (int i = 0; i < LIMIT && current != null; i++) {
            println(current.getAddress() + "  " + current);
            current = current.getNext();
        }
        StringBuilder functions = new StringBuilder();
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            functions.append(f.getEntryPoint()).append(' ');
        }
        println("function_entries=" + functions);
    }
}
