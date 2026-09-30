"""Protocol for the logical primitives a code provides to generic constructions."""

from typing import no_type_check

from guppylang import guppy
from guppylang.std.builtins import owned

__all__ = ["CodePrimitives"]


@guppy.protocol
class CodePrimitives[Q]:
    """Logical primitives of a code acting on its logical qubit type.

    Type parameters:
        Q: The code's logical qubit type.
    """

    @guppy.require
    @no_type_check
    def prep_zero(self) -> Q:
        """Prepare a qubit in the logical zero state."""

    @guppy.require
    @no_type_check
    def prep_noisy_t(self) -> Q:
        r"""Prepare a qubit in the logical :math:`T\ket{+}` state, not necessarily
        fault-tolerantly."""

    @guppy.require
    @no_type_check
    def x(self, q: Q) -> None:
        """Apply a logical X gate."""

    @guppy.require
    @no_type_check
    def z(self, q: Q) -> None:
        """Apply a logical Z gate."""

    @guppy.require
    @no_type_check
    def h(self, q: Q) -> None:
        """Apply a logical H gate."""

    @guppy.require
    @no_type_check
    def sdg(self, q: Q) -> None:
        """Apply a logical S dagger gate."""

    @guppy.require
    @no_type_check
    def cx(self, ctl: Q, tgt: Q) -> None:
        """Apply a logical CX gate."""

    @guppy.require
    @no_type_check
    def measure_z(self, q: Q @ owned) -> bool:
        """Measure the qubit in the logical Z basis and return the decoded outcome."""

    @guppy.require
    @no_type_check
    def discard(self, q: Q @ owned) -> None:
        """Discard the qubit."""
