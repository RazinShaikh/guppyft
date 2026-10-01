"""Logical primitives a code provides to generic constructions."""

from guppylang import guppy
from guppylang.std.lang import Function, owned

__all__ = ["CodePrimitives"]


@guppy.struct(frozen=True)
class CodePrimitives[Q, M]:  # type: ignore[misc]
    r"""Logical primitives of a code, given as the code's own functions.

    Construct with positional arguments in the attribute order below, e.g.
    `CodePrimitives(prep_noisy_t, h, sdg, z, cx, measure_z, decode)`. Guppy structs
    take no keyword arguments, and `h`, `sdg` and `z` share a type, so a wrong order
    still type checks.

    Type parameters:
        Q: The code's logical qubit type.
        M: The code's logical measurement type, decoded with `decode`.

    Attributes:
        prep_noisy_t: Prepare a qubit in the logical :math:`T\ket{+}` state, not
            necessarily fault-tolerantly.
        h: Apply a logical H gate.
        sdg: Apply a logical S dagger gate.
        z: Apply a logical Z gate.
        cx: Apply a logical CX gate, given the control then the target.
        measure_z: Measure the qubit in the logical Z basis, without decoding.
        decode: Decode a logical measurement outcome.
    """

    prep_noisy_t: Function[[], Q]  # type: ignore[type-arg,valid-type]
    h: Function[[Q], None]  # type: ignore[type-arg,valid-type,misc]
    sdg: Function[[Q], None]  # type: ignore[type-arg,valid-type,misc]
    z: Function[[Q], None]  # type: ignore[type-arg,valid-type,misc]
    cx: Function[[Q, Q], None]  # type: ignore[type-arg,valid-type]
    measure_z: Function[[Q @ owned], M]  # type: ignore[type-arg,valid-type,misc]
    decode: Function[[M @ owned], bool]  # type: ignore[type-arg,valid-type,misc]
