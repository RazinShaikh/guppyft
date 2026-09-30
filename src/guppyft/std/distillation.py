"""Magic state distillation built from a code's `CodePrimitives`."""

from typing import no_type_check

from guppylang import guppy
from guppylang.std.builtins import array, comptime, owned
from guppylang.std.lang import Drop
from guppylang.std.option import Option, nothing, some

from .code_primitives import CodePrimitives

__all__ = [
    "Distillation15To1",
]

_N_BLOCKS = 16
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
def _checks_pass(outcomes: array[bool, comptime(_N_BLOCKS)]) -> bool:
    for support in comptime(_X_CHECK_SUPPORTS):
        parity = False
        for j in support:
            parity ^= outcomes[j]
        if parity:
            return False
    return True


@guppy
@no_type_check
def _parity(outcomes: array[bool, comptime(_N_BLOCKS)]) -> bool:
    parity = False
    for j in range(1, comptime(_N_BLOCKS)):
        parity ^= outcomes[j]
    return parity


@guppy
@no_type_check
def _inject_tdg[Q, Ops: CodePrimitives[Q]](
    ops: Ops,
    q: Q,
    t_state: Q @ owned,
) -> None:
    r"""Apply T dagger to `q` by consuming a :math:`T\ket{+}` state."""
    ops.cx(q, t_state)
    if not ops.measure_z(t_state):
        ops.sdg(q)


@guppy.struct
class Distillation15To1[
    Q,
    Ops: (CodePrimitives[Q], Drop),  # type: ignore[name-defined]
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
    def prepare(self) -> Option[Q]:
        r"""Attempt one distillation round.

        Returns the distilled :math:`T\ket{+}` qubit, or `nothing` if a check failed.
        """
        qs = array(self.ops.prep_zero() for _ in range(comptime(_N_BLOCKS)))
        for i in comptime(_PLUS_IDXS):
            self.ops.h(qs[i])
        for c, t in comptime(_ENCODER_CX_PAIRS):
            self.ops.cx(qs[c], qs[t])

        outcomes = array(False for _ in range(comptime(_N_BLOCKS)))
        for j in range(1, comptime(_N_BLOCKS)):
            t_state = self.ops.prep_noisy_t()
            _inject_tdg(self.ops, qs[j], t_state)
            self.ops.h(qs[j])
            outcomes[j] = self.ops.measure_z(qs.take(j))

        out = qs.take(0)
        qs.discard_all_taken()

        if not _checks_pass(outcomes):
            self.ops.discard(out)
            return nothing()

        if _parity(outcomes):
            self.ops.z(out)
        return some(out)
