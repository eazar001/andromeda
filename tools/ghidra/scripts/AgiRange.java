// Disassemble and print explicit address ranges, for code that is not part of a recovered function.
// Arguments: <report path> <start>-<end>...
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import java.io.PrintWriter;
import java.util.HexFormat;

public class AgiRange extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        try (PrintWriter out = new PrintWriter(args[0])) {
            for (int i = 1; i < args.length; i++) {
                String[] bounds = args[i].split("-");
                print(out, toAddr(bounds[0]), toAddr(bounds[1]));
            }
        }
    }

    private void print(PrintWriter out, Address start, Address end) throws Exception {
        out.println("==== " + start + " - " + end);
        Address cursor = start;
        while (cursor.compareTo(end) <= 0) {
            Instruction ins = getInstructionAt(cursor);
            if (ins == null) {
                disassemble(cursor);
                ins = getInstructionAt(cursor);
            }
            if (ins == null) {
                out.printf("%s  %02x%n", cursor, currentProgram.getMemory().getByte(cursor));
                cursor = cursor.add(1);
                continue;
            }
            out.printf("%s  %-14s %s%n", ins.getAddress(), HexFormat.of().formatHex(ins.getBytes()), ins);
            cursor = cursor.add(ins.getLength());
        }
    }
}
