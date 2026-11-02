// Read-only: list instructions whose text contains any given token.
// Arguments: <report path> <token>...
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import java.io.PrintWriter;
import java.util.Arrays;
import java.util.List;

public class AgiGrep extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        List<String> tokens = Arrays.asList(args).subList(1, args.length);
        try (PrintWriter out = new PrintWriter(args[0])) {
            for (Instruction ins : currentProgram.getListing().getInstructions(true)) {
                String text = ins.toString();
                if (tokens.stream().anyMatch(t -> text.contains(t + "]") || text.endsWith(t))) {
                    Function f = getFunctionContaining(ins.getAddress());
                    out.println(ins.getAddress() + "  " + text + "  in " + (f == null ? "?" : f.getName()));
                }
            }
        }
    }
}
