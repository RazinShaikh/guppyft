"""Protocol for the logical primitives a code provides to generic constructions."""

from typing import Any, no_type_check

from guppylang import guppy
from guppylang.std.builtins import owned

__all__ = ["CodePrimitives", "code_primitives_from"]


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


def code_primitives_from(
    qubit_type: Any,
    *,
    prep_zero: Any,
    prep_noisy_t: Any,
    x: Any,
    z: Any,
    h: Any,
    sdg: Any,
    cx: Any,
    measure_z: Any,
    discard: Any,
) -> type:
    """Build a struct implementing `CodePrimitives[qubit_type]` from Guppy functions.

    Each argument must be a Guppy function (or op) with the signature of the protocol
    method of the same name, without `self`. Call once per code at module level, as
    each call defines a new Guppy type.
    """
    # Renamed so the method definitions below do not shadow them.
    Q = qubit_type
    prep_zero_fn, prep_noisy_t_fn = prep_zero, prep_noisy_t
    x_fn, z_fn, h_fn, sdg_fn, cx_fn = x, z, h, sdg, cx
    measure_z_fn, discard_fn = measure_z, discard

    @guppy.struct
    class CodePrimitivesImpl:
        @guppy
        @no_type_check
        def prep_zero(self) -> Q:
            return prep_zero_fn()

        @guppy
        @no_type_check
        def prep_noisy_t(self) -> Q:
            return prep_noisy_t_fn()

        @guppy
        @no_type_check
        def x(self, q: Q) -> None:
            x_fn(q)

        @guppy
        @no_type_check
        def z(self, q: Q) -> None:
            z_fn(q)

        @guppy
        @no_type_check
        def h(self, q: Q) -> None:
            h_fn(q)

        @guppy
        @no_type_check
        def sdg(self, q: Q) -> None:
            sdg_fn(q)

        @guppy
        @no_type_check
        def cx(self, ctl: Q, tgt: Q) -> None:
            cx_fn(ctl, tgt)

        @guppy
        @no_type_check
        def measure_z(self, q: Q @ owned) -> bool:
            return measure_z_fn(q)

        @guppy
        @no_type_check
        def discard(self, q: Q @ owned) -> None:
            discard_fn(q)

    return CodePrimitivesImpl
