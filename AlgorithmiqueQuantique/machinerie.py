import math
from typing import Dict, List, Literal, Optional, Sequence, cast

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit.circuit import Bit, Register
from qiskit.circuit.library import CXGate, MCMTGate, ZGate
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import Statevector
from qiskit_aer import Aer

flag = [1, 1, 0, 1, 1, 0]


class Circuit(QuantumCircuit):
    def __init__(self, *regs: Register | int | Sequence[Bit], **kwargs):
        super().__init__(*regs, **kwargs)

    def draw_circuit(
        self, output: Literal["mpl", "latex", "none"] = "mpl", **kwargs
    ) -> None:
        match output:
            case "none":
                self.draw(**kwargs)
            case "mpl":
                _ = self.draw(style="clifford", output=output, **kwargs)
            case _:
                _ = self.draw(output=output, **kwargs)

    def draw_qubits(
        self,
        output: Literal["bloch", "latex", "city", "hinton", "qsphere"] = "latex",
        **kwargs,
    ):
        psi = Statevector(self)
        if output == "latex":
            return psi.draw(output, **kwargs)
        else:
            _ = psi.draw(output, **kwargs)

    def get_measure(
        self,
        input_qubit: Optional["Circuit"] = None,
        qbits: Optional[List[int]] = None,
        shots: int = 1024,
        normalise: bool = True,
        plot_full_circuit: bool = False,
    ) -> Dict[str, Dict[str, int | float]] | Dict[str, int | float]:
        if input_qubit is not None:
            input_qubit.barrier()

            composition = cast(
                QuantumCircuit, self.compose(input_qubit, front=True, copy=True)
            )
        else:
            composition = self.copy()
        if qbits is not None:
            composition.add_register(ClassicalRegister(len(qbits)))

            for i, j in enumerate(qbits):
                composition.measure(j, i)

            if plot_full_circuit:
                _ = composition.draw(style="clifford", output="mpl")

            results = (
                StatevectorSampler().run([composition], shots=shots).result()[0].data
            )

            if normalise and shots > 0:
                counts = {
                    k: {kk: vv / shots for kk, vv in v.get_counts().items()}
                    for k, v in results.items()
                }
            else:
                counts = {k: v.get_counts() for k, v in results.items()}
            if len(counts) == 1:
                return list(counts.values())[0]
            else:
                return counts
        else:
            circ = self.copy()
            circ.measure_all()
            results = (
                StatevectorSampler()
                .run([circ], shots=shots)
                .result()[0]
                .data.meas.get_counts()  # type: ignore
            )
            if normalise and shots > 0:
                return {k: v / shots for k, v in results.items()}
            return results

    def get_unitary(self) -> np.ndarray:
        simulator = Aer.get_backend("aer_simulator")
        circ = transpile(self.copy(), simulator)
        circ.save_unitary()  # type: ignore
        result = simulator.run(circ).result()  # type: ignore
        unitary = result.get_unitary(circ)
        return np.asarray(unitary)

    @classmethod
    def from_unitary(cls, matrix: np.ndarray, n_qubits: int) -> "Circuit":
        temp_circ = cls(n_qubits)
        temp_circ.unitary(matrix, range(n_qubits))
        return temp_circ

    def get_flat_unitary(self) -> List[float]:
        flattened = []
        for row in self.get_unitary():
            for val in row:
                flattened.append(float(val.real))
                flattened.append(float(val.imag))
        return flattened

    @classmethod
    def from_flat_unitary(cls, matrix: List[float], n_qubits: int) -> "Circuit":
        assert math.log(len(matrix) / 2) / math.log(4) == float(n_qubits)

        matrix_size = 2**n_qubits
        expected_length = 2 * matrix_size**2

        assert len(matrix) == expected_length

        unitary = np.zeros((matrix_size, matrix_size), dtype=complex)

        idx = 0
        for i in range(matrix_size):
            for j in range(matrix_size):
                real = matrix[idx]
                imag = matrix[idx + 1]
                unitary[i, j] = complex(real, imag)
                idx += 2

        u_dag_u = np.conjugate(unitary.T) @ unitary
        identity = np.eye(matrix_size)

        assert np.allclose(u_dag_u, identity, atol=1e-6), "not unitary"
        return cls.from_unitary(unitary, n_qubits)

    @classmethod
    def from_angles(cls, angles: List[float]) -> "Circuit":
        qc = cls(len(angles) // 3)
        for i in range(0, len(angles), 3):
            qc.u(theta=angles[i], phi=angles[i + 1], lam=angles[i + 2], qubit=i // 3)
        return qc


def create_zf(flag: List[int]) -> Circuit:
    n = len(flag)
    qc = Circuit(n, name="zf")

    for i, j in enumerate(flag):
        if j == 0:
            qc.x(i)

    qc.compose(MCMTGate(ZGate(), n - 1, 1), inplace=True)

    for i, j in enumerate(flag):
        if j == 0:
            qc.x(i)

    return qc


def create_zor(n: int) -> Circuit:
    zor = Circuit(n, name="Zor")
    zor.x(range(n))
    zor.h(n - 1)
    zor.compose(MCMTGate(CXGate(), n - 1, 1), inplace=True)
    zor.h(n - 1)
    zor.x(range(n))
    return zor


def create_grover(
    flag: List[int],
    hadamard_middle: List[int],
    hadamard_end: List[int],
) -> Circuit:
    n = len(flag)

    grover = Circuit(n)
    zf = create_zf(flag)

    zor = create_zor(n)

    grover.append(zf.to_gate(), range(n))
    if len(hadamard_middle) > 0:
        grover.h(hadamard_middle)
    grover.append(zor.to_gate(), range(n))
    if len(hadamard_end) > 0:
        grover.h(hadamard_end)

    return grover


def test_flag_grover(
    flag: List[int],
    input_qubits: Circuit,
    hadamard_middle: List[int],
    hadamard_end: List[int],
):
    n = len(flag)

    try:
        assert len(hadamard_end) <= n - 2, "Trop de hadamard end"
        assert len(hadamard_middle) <= n - 2, "Trop de hadamard middle"
        for x in hadamard_end:
            assert isinstance(x, int) and x >= 0 and x < n, (
                "Un élément étrange dans hadamard end"
            )
        for x in hadamard_middle:
            assert isinstance(x, int) and x >= 0 and x < n, (
                "Un élément étrange dans hadamard middle"
            )
    except AssertionError as e:
        return str(e)

    qc = Circuit(n)

    qc.compose(input_qubits, inplace=True)
    qc.compose(create_grover(flag, hadamard_middle, hadamard_end), inplace=True)

    return str(qc.get_measure())


def draw404(**kwargs) -> None:
    qc = Circuit(
        QuantumRegister(1, "x"),
        QuantumRegister(1, "y"),
        QuantumRegister(1, "z"),
        QuantumRegister(1, "s"),
    )
    qc.append(Circuit(1, name="4").to_gate(), [1])
    qc.swap(2, 3)
    qc.append(Circuit(1, name="0").to_gate(), [2])
    qc.cx(1, 0)
    qc.append(Circuit(2, name="4").to_gate(), [0, 1])
    qc.barrier()

    qc.append(Circuit(1, name="C").to_gate(), [1])
    qc.swap(2, 3)
    qc.t(2)
    qc.append(Circuit(3, name="F").to_gate(), [0, 1, 2])

    if kwargs.get("return_fig", False):
        kwargs.pop("return_fig")
        return qc.draw_circuit(**kwargs)
    qc.draw_circuit(**kwargs)


def q(x: str | List[int]) -> Circuit:
    qc = Circuit(len(x))
    for i, j in enumerate(x):
        if str(j) == "1":
            qc.x(i)
    return qc
