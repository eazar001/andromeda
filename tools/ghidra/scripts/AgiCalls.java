// Read-only: list every indirect CALL/JMP through memory or a register, with its containing function.
// Arguments: <report path>
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import java.io.PrintWriter;

public class AgiCalls extends GhidraScript {
    @Override
    public void run() throws Exception {
        try (PrintWriter out = new PrintWriter(getScriptArgs()[0])) {
            for (Instruction ins : currentProgram.getListing().getInstructions(true)) {
                String text = ins.toString();
                boolean branch = text.startsWith("CALL") || text.startsWith("JMP");
                if (branch && (text.contains("[") || !text.contains("0x"))) {
                    Function f = getFunctionContaining(ins.getAddress());
                    out.println(ins.getAddress() + "  " + text + "  in " + (f == null ? "?" : f.getEntryPoint()));
                }
            }
        }
    }
}
