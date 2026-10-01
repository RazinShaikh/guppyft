"""Magic state distillation built from a code's `CodePrimitives`."""

from typing import no_type_check

from guppylang import guppy
from guppylang.std.builtins import array, comptime, owned
from guppylang.std.lang import Copy, Drop
from guppylang.std.option import Option, nothing, some

from .code_primitives import CodePrimitives
from .state_factory import PreBlock

__all__ = [
    "Distillation15To1",
    "DistillationFlags",
]

_N_BLOCKS = 16
_N_OUTCOMES = _N_BLOCKS - 1
_PLUS_IDXS = [0, 1, 2, 4, 8]

# CX layers encoding the first-order Reed-Muller state on 16 blocks.
# fmt: off
_ENCODER_CX_PAIRS = [
    (1, 9), (2, 10), (4, 12),
    (0, 4), (1, 5), (2, 6),
    (8, 12), (9, 13), (10, 14),
    (0, 2), (1, 3),
    (4, 6), (5, 7),
    (8, 10), (9, 11),
    (12, 14), (13, 15),
    (0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11), (12, 13), (14, 15),
]
# fmt: on

# Blocks whose X outcomes form each X stabilizer of the 15-qubit code.
# https://errorcorrectionzoo.org/c/stab_15_1_3
_X_CHECK_SUPPORTS = [
    [1, 3, 5, 7, 9, 11, 13, 15],
    [2, 3, 6, 7, 10, 11, 14, 15],
    [4, 5, 6, 7, 12, 13, 14, 15],
    [8, 9, 10, 11, 12, 13, 14, 15],
]


@guppy
@no_type_check
def _checks_pass(bits: array[bool, comptime(_N_OUTCOMES)]) -> bool:
    for support in comptime(_X_CHECK_SUPPORTS):
        parity = False
        for j in support:
            # Block 0 is not measured, so block `j` is at index `j - 1`.
            parity ^= bits[j - 1]
        if parity:
            return False
    return True


@guppy
@no_type_check
def _parity(bits: array[bool, comptime(_N_OUTCOMES)]) -> bool:
    parity = False
    for i in range(comptime(_N_OUTCOMES)):
        parity ^= bits[i]
    return parity


@guppy
@no_type_check
def _inject_tdg[Q, M: Drop, Ops: CodePrimitives[Q, M]](
    ops: Ops,
    q: Q,
    t_state: Q @ owned,
) -> None:
    r"""Apply T dagger to `q` by consuming a :math:`T\ket{+}` state."""
    ops.cx(q, t_state)
    m = ops.measure_z(t_state)
    if not ops.decode(m):
        ops.sdg(q)


@guppy.struct
class DistillationFlags[M, Ops]:
    """Unread X-basis outcomes of a 15-to-1 distillation round.

    Attributes:
        ops: The code's primitives, used to decode the outcomes and correct the output.
        outcomes: Measurement outcomes of blocks 1 to 15.
    """

    ops: Ops
    outcomes: array[M, comptime(_N_OUTCOMES)]  # type: ignore[valid-type]


@guppy
@no_type_check
def _distillation_check[Q, M: Drop, Ops: (CodePrimitives[Q, M], Drop)](
    q: Q @ owned, flags: DistillationFlags[M, Ops] @ owned
) -> Option[Q]:
    """Check if the distilled state passes the X stabilizer checks.
    If the checks pass, returns `some(q)` with the corrected state.
    """
    ops = flags.ops
    bits = array(ops.decode(m) for m in flags.outcomes)
    if not _checks_pass(bits):
        ops.discard(q)
        return nothing()
    if _parity(bits):
        ops.z(q)
    return some(q)


@guppy
@no_type_check
def _distillation_discard[Q, M: Drop, Ops: (CodePrimitives[Q, M], Drop)](
    q: Q @ owned, flags: DistillationFlags[M, Ops] @ owned
) -> None:
    flags.ops.discard(q)


@guppy.struct
class Distillation15To1[
    Q,
    M: Drop,
    Ops: (CodePrimitives[Q, M], Copy, Drop),  # type: ignore[name-defined]
]:
    r"""15-to-1 :math:`T\ket{+}` distillation using the [[15, 1, 3]] Reed-Muller code.

    Qubit 0 is entangled with a 15-qubit Reed-Muller code block, on which transversal
    T dagger (via noisy :math:`T\ket{+}` injection) acts as a logical T. Measuring the
    15 qubits in the X basis teleports :math:`T\ket{+}` onto qubit 0, and the X
    stabilizer parities detect faulty injections.

    Circuit taken from Fig. 8 of:
    https://journals.aps.org/prxquantum/pdf/10.1103/PRXQuantum.2.020341

    Attributes:
        ops: The code's primitives used to implement the circuit.
    """

    ops: Ops

    @guppy
    @no_type_check
    def prepare(
        self, qs: array[Q, comptime(_N_BLOCKS)] @ owned
    ) -> PreBlock[Q, DistillationFlags[M, Ops]]:
        r"""Run one distillation round without reading the X-basis outcomes.

        Calling `force_check` on the result reads the outcomes, and returns the
        distilled :math:`T\ket{+}` state, or `nothing` if a check failed.

        Args:
            qs: 16 qubits in the logical zero state, consumed by the round.
        """
        for i in comptime(_PLUS_IDXS):
            self.ops.h(qs[i])
        for c, t in comptime(_ENCODER_CX_PAIRS):
            self.ops.cx(qs[c], qs[t])

        for j in range(1, comptime(_N_BLOCKS)):
            t_state = self.ops.prep_noisy_t()
            _inject_tdg(self.ops, qs[j], t_state)
            self.ops.h(qs[j])

        outcomes = array(
            self.ops.measure_z(qs.take(i + 1)) for i in range(comptime(_N_OUTCOMES))
        )
        out = qs.take(0)
        qs.discard_all_taken()

        return PreBlock(
            out,
            DistillationFlags(self.ops, outcomes),
            _distillation_check,
            _distillation_discard,
        )
