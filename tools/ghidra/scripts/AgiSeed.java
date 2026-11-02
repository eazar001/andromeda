// Load AGIDATA.OVL into the data segment, then disassemble and name table-reachable handlers.
// Arguments: <seed file> <AGIDATA.OVL>
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import java.nio.file.Files;
import java.nio.file.Path;

public class AgiSeed extends GhidraScript {
    private static final String DATA_ADDRESS = "19f5:0000";

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        loadOverlay(Path.of(args[1]));
        int created = 0;
        for (String line : Files.readAllLines(Path.of(args[0]))) {
            String[] parts = line.trim().split(" ");
            Address address = toAddr(parts[0]);
            disassemble(address);
            if (getFunctionAt(address) == null && createFunction(address, null) != null) {
                created++;
            }
            createLabel(address, parts[1], false, SourceType.USER_DEFINED);
        }
        println("functions_created=" + created);
    }

    private void loadOverlay(Path overlay) throws Exception {
        Memory memory = currentProgram.getMemory();
        Address start = toAddr(DATA_ADDRESS);
        MemoryBlock block = memory.getBlock(start);
        if (!block.isInitialized()) {
            block = memory.convertToInitialized(block, (byte) 0);
        }
        byte[] bytes = Files.readAllBytes(overlay);
        int length = (int) Math.min(block.getSize(), bytes.length);
        memory.setBytes(start, bytes, 0, length);
        println("overlay_bytes_loaded=" + length + " of " + bytes.length);
    }
}
