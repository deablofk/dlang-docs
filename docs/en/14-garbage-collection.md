# Garbage Collection

DLang has **no garbage collector**, and that is a deliberate design decision, not a missing feature. A systems language should make the cost of memory visible and predictable; a background collector that can pause your program at an unpredictable moment is the opposite of that.

What DLang has *instead* is stronger than a collector: **static ownership**. Every allocation belongs to exactly one owning value, and the compiler inserts the release at that owner's last use — at compile time, with zero runtime machinery. You get the two things a GC is prized for — "I don't write frees" and "I can't get it wrong" — without pauses, without headers on objects, and without a runtime.

## How memory actually gets freed

Three mechanisms cover everything, all static ([Memory Safety](14a-memory-safety.md) has the full model):

- **ASAP destruction.** A `nocopy` owner with a `deinit` (every container: `List`, `Map`, `ByteBuf`, `Pool`, and your own resource wrappers) is destroyed **at its last use** — not scope end, not "eventually". No drop flags, no reference counts; the analysis proves the release point per control-flow path.

```dlang
process :: () {
  var xs: List(int) = List(int).empty()
  xs.add(1)
  xs.add(2)
  println("${xs.size()}")     // last use of xs — its buffer is freed right here
  expensiveWorkThatNeedsMemory()
}
```

- **String reclamation.** `string` temporaries — concatenation chains, interpolation, `println` arguments, `s = s + piece` accumulation loops — are freed on the spot by compiler-inserted drops. The natural way to build a string is also the memory-correct way.

- **Move semantics.** Ownership transfers (`val ys = xs`, `sink` parameters, returns) are moves, so there is never a second owner to "collect" — and never a moment where two things might free the same buffer (`E_USE_AFTER_MOVE` guards the source binding).

The net effect is deterministic, prompt reclamation: memory pressure tracks your program's live data, release points are readable from the source, and a profiler sees your allocations, not a collector's.

## What a GC gives you that DLang refuses

Tracing collectors exist to support **unrestricted aliasing** — any object may point at any other, and the runtime figures out liveness. DLang deliberately does not have unrestricted aliasing: values are values, references are second-class, and shared identity goes through `Pool(T)` handles or indices ([Memory Safety](14a-memory-safety.md#graphs-and-shared-identity--poolt--handle-or-indices)). Once aliasing is structured, liveness is decidable at compile time and the collector has nothing left to do.

Cycles — the classic GC selling point — illustrate it: entities in a `Pool` may reference each other freely through copyable `Handle` values, and the *pool* (one owner) dies at its last use. No cycle detector needed, because handles are data, not edges the runtime must trace.

## Leak checking is a tool, not a tax

The compiler's guarantee is per-owner: every owner is destroyed exactly once. The remaining question a developer sometimes has — "what is still live right now, and who allocated it?" — is answered by tooling on the *Builtin floor* (a `debugAllocator` used by the compiler's own proof harnesses), not by a runtime you ship. Release binaries carry no tracking machinery at all.

## Why no collector — the summary

| | Tracing GC | DLang |
|---|---|---|
| who frees | runtime, eventually | compiler, at last use |
| pauses | yes (or complex incremental machinery) | none |
| per-object cost | headers, barriers, scanning | zero |
| cycles | traced at runtime | structured away (`Pool` handles) |
| leak = | unreachable-but-retained memory | ruled out per owner at compile time |
| when memory returns | unpredictable | deterministic, readable from source |

## Related

- [Memory Safety](14a-memory-safety.md) — the ownership model in full
- [Manual Memory — the Builtin floor](13-manual-memory.md)
- [Dynamic Allocation — owning values](18-dynamic-allocation.md)

[← Index](README.md)
