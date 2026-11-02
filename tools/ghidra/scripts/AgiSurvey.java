// Read-only survey of the loaded program: blocks, code coverage, functions, errors, strings.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.MemoryBlock;
import java.util.Iterator;
import java.util.TreeMap;

public class AgiSurvey extends GhidraScript {
    private static final long BUCKET = 4096;

    @Override
    public void run() {
        println("language=" + currentProgram.getLanguageID() + " compiler=" + currentProgram.getCompilerSpec().getCompilerSpecID());
        reportBlocks();
        reportCoverage();
        reportFunctions();
        reportBookmarks("Error");
        reportBookmarks("Warning");
        reportStrings();
    }

    private void reportBlocks() {
        for (MemoryBlock b : currentProgram.getMemory().getBlocks()) {
            println("block " + b.getName() + " " + b.getStart() + "-" + b.getEnd() + " size=" + b.getSize() + " init=" + b.isInitialized() + " x=" + b.isExecute());
        }
    }

    private void reportCoverage() {
        TreeMap<Long, Long> perBucket = new TreeMap<>();
        long total = 0;
        for (Instruction i : currentProgram.getListing().getInstructions(true)) {
            perBucket.merge(i.getAddress().getOffset() / BUCKET, (long) i.getLength(), Long::sum);
            total += i.getLength();
        }
        println("instruction_bytes=" + total + " of_initialized=" + currentProgram.getMemory().getLoadedAndInitializedAddressSet().getNumAddresses());
        println("instruction_bytes_per_4K=" + perBucket);
    }

    private void reportFunctions() {
        int count = 0;
        StringBuilder largest = new StringBuilder();
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            count++;
            if (f.getBody().getNumAddresses() > 600) {
                largest.append(f.getEntryPoint()).append(':').append(f.getBody().getNumAddresses()).append(' ');
            }
        }
        println("functions=" + count + " over_600_bytes=" + largest);
        Iterator<Address> entries = currentProgram.getSymbolTable().getExternalEntryPointIterator();
        while (entries.hasNext()) {
            println("entry=" + entries.next());
        }
    }

    private void reportBookmarks(String type) {
        int count = 0;
        StringBuilder sample = new StringBuilder();
        var bookmarks = currentProgram.getBookmarkManager().getBookmarksIterator(type);
        while (bookmarks.hasNext()) {
            var b = bookmarks.next();
            if (count++ < 8) {
                sample.append(b.getAddress()).append(" [").append(b.getComment()).append("]; ");
            }
        }
        println(type + "_bookmarks=" + count + " sample=" + sample);
    }

    private void reportStrings() {
        int count = 0;
        for (Data d : currentProgram.getListing().getDefinedData(true)) {
            if (d.hasStringValue()) {
                count++;
            }
        }
        println("defined_strings=" + count);
    }
}
