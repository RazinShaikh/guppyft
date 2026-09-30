"""Protocol for the logical primitives a code provides to generic constructions."""

from typing import no_type_check

from guppylang import guppy
from guppylang.std.builtins import nat, owned

from ._logical_block import LogicalBlock

__all__ = ["CodePrimitives"]


@guppy.protocol
class CodePrimitives[BLOCK_SIZE: nat]:
    """Logical primitives of a code acting on `LogicalBlock[BLOCK_SIZE]`.

    Type parameters:
        BLOCK_SIZE: Number of physical qubits in a logical block.
    """

    @guppy.require
    @no_type_check
    def prep_zero(self) -> LogicalBlock[BLOCK_SIZE]:
        """Prepare a block in the logical zero state."""

    @guppy.require
    @no_type_check
    def prep_noisy_t(self) -> LogicalBlock[BLOCK_SIZE]:
        r"""Prepare a block in the logical :math:`T\ket{+}` state, not necessarily
        fault-tolerantly."""

    @guppy.require
    @no_type_check
    def x(self, blk: LogicalBlock[BLOCK_SIZE]) -> None:
        """Apply a logical X gate."""

    @guppy.require
    @no_type_check
    def z(self, blk: LogicalBlock[BLOCK_SIZE]) -> None:
        """Apply a logical Z gate."""

    @guppy.require
    @no_type_check
    def h(self, blk: LogicalBlock[BLOCK_SIZE]) -> None:
        """Apply a logical H gate."""

    @guppy.require
    @no_type_check
    def sdg(self, blk: LogicalBlock[BLOCK_SIZE]) -> None:
        """Apply a logical S dagger gate."""

    @guppy.require
    @no_type_check
    def cx(self, ctl: LogicalBlock[BLOCK_SIZE], tgt: LogicalBlock[BLOCK_SIZE]) -> None:
        """Apply a logical CX gate."""

    @guppy.require
    @no_type_check
    def measure_z(self, blk: LogicalBlock[BLOCK_SIZE] @ owned) -> bool:
        """Measure the block in the logical Z basis and return the decoded outcome."""
