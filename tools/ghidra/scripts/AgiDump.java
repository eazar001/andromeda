// Read-only: for each address argument, write the containing function's listing and decompilation to a report file.
// Arguments: <report path> <address>...
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.util.task.ConsoleTaskMonitor;
import java.io.PrintWriter;
import java.util.HexFormat;

public class AgiDump extends GhidraScript {
    private static final int DECOMPILE_TIMEOUT_SECONDS = 60;

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        DecompInterface decompiler = new DecompInterface();
        decompiler.openProgram(currentProgram);
        try (PrintWriter out = new PrintWriter(args[0])) {
            for (int i = 1; i < args.length; i++) {
                dump(out, decompiler, args[i]);
            }
        } finally {
            decompiler.dispose();
        }
    }

    private void dump(PrintWriter out, DecompInterface decompiler, String address) throws Exception {
        Function function = getFunctionContaining(currentProgram.getAddressFactory().getAddress(address));
        out.println("==== " + address + " -> " + (function == null ? "no function" : function.getEntryPoint() + " size=" + function.getBody().getNumAddresses()));
        if (function == null) {
            return;
        }
        for (Instruction ins : currentProgram.getListing().getInstructions(function.getBody(), true)) {
            out.printf("%s  %-14s %s%n", ins.getAddress(), HexFormat.of().formatHex(ins.getBytes()), ins);
        }
        DecompileResults result = decompiler.decompileFunction(function, DECOMPILE_TIMEOUT_SECONDS, new ConsoleTaskMonitor());
        out.println(result.decompileCompleted() ? result.getDecompiledFunction().getC() : "decompile failed: " + result.getErrorMessage());
    }
}
