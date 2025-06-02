from typing import Dict, List, Tuple

from pydantic import BaseModel, ValidationError

from machinerie import Circuit, q, test_flag_grover

flag_grover_1 = [0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0]
flag_grover_2 = [0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1]


class GroverInput(BaseModel):
    input_qubits: List[float]
    hadamard_middle: List[int]
    hadamard_end: List[int]


def iszero(x, eps=1e-5) -> bool:
    return abs(x) < eps


def challenge_1(data: Dict[str, List[float]]) -> Tuple[bool, str]:
    p1_input = Circuit.from_flat_unitary(data["p1_input"], 1)

    p1_mesure = p1_input.get_measure(shots=10000)

    try:
        assert iszero(p1_mesure.get("1", 0) - 0.75, eps=0.05), (
            f"p1 a une probabilité de {p1_mesure.get('1', 0)} de donner 1, au lieu de 0.75"
        )
        assert iszero(p1_mesure.get("0", 0) - 0.25, eps=0.05), (
            f"p1 a une probabilité de {p1_mesure.get('0', 0)} de donner 0, au lieu de 0.25"
        )

    except AssertionError as e:
        return False, str(e)

    p2 = Circuit(2)
    p2.h(0)
    p2.cx(0, 1)

    p2_input = Circuit.from_flat_unitary(data["p2_input"], 2)
    p2.compose(p2_input, front=True, inplace=True)

    p2_measure = p2.get_measure(shots=10000)
    p2_input_measure = p2_input.get_measure(shots=10000)

    success = True

    for k, v in p2_measure.items():
        if k not in p2_input_measure:
            success = False
        else:
            success = success and iszero(p2_input_measure[k] - v, eps=0.01)

    if not success:
        return (
            False,
            f"p2 et p2_input ne donnent pas les mêmes résultats à la mesure : {p2_measure} et {p2_input_measure}",
        )

    return success, ""


def challenge_2(data: Dict[str, List[float]]) -> Tuple[bool, str]:
    f1 = Circuit.from_flat_unitary(data["f1"], 2)
    f1_measure_0 = f1.get_measure(q("00"), qbits=[1]).get("1", 0)
    f1_measure_1 = f1.get_measure(q("10"), qbits=[1]).get("0", 0)

    f2 = Circuit.from_flat_unitary(data["f2"], 3)
    f2_measure_00 = f2.get_measure(q("00"), qbits=[2]).get("1", 0)
    f2_measure_01 = f2.get_measure(q("01"), qbits=[2]).get("0", 0)
    f2_measure_10 = f2.get_measure(q("10"), qbits=[2]).get("1", 0)
    f2_measure_11 = f2.get_measure(q("11"), qbits=[2]).get("0", 0)

    full_circuit = Circuit(2)
    full_circuit.h([0, 1])
    grover = Circuit.from_flat_unitary(data["grover"], 2)
    full_circuit.compose(grover, inplace=True)
    grover_measure = full_circuit.get_measure().get("10", 0)

    try:
        assert f1_measure_0 == 1.0, (
            f"f1 mesuré en 1 avec x = 0 en entrée donne {f1_measure_0} au lieu de 1"
        )
        assert f1_measure_1 == 1.0, (
            f"f1 mesuré en 0 avec x = 1 en entrée donne {f1_measure_1} au lieu de 1"
        )

        assert f2_measure_00 == 1.0, (
            f"f2 mesuré en 1 avec x = 00 en entrée donne {f2_measure_00} au lieu de 1"
        )
        assert f2_measure_01 == 1.0, (
            f"f2 mesuré en 0 avec x = 01 en entrée donne {f2_measure_01} au lieu de 1"
        )
        assert f2_measure_10 == 1.0, (
            f"f2 mesuré en 1 avec x = 10 en entrée donne {f2_measure_10} au lieu de 1"
        )
        assert f2_measure_11 == 1.0, (
            f"f2 mesuré en 0 avec x = 11 en entrée donne {f2_measure_11} au lieu de 1"
        )

        assert grover_measure == 1.0, (
            f"grover mesuré donne une probabilité de {grover_measure} pour |10>, au lieu de 1"
        )
    except AssertionError as e:
        return False, str(e)

    return True, ""


def challenge_grover_1(data: Dict[str, List[float] | List[int]]) -> str:
    try:
        grover_inputs = GroverInput(**data)  # type: ignore
    except ValidationError as e:
        return str(e)
    except Exception as e:
        return str(e)

    input_qubits = Circuit.from_angles(grover_inputs.input_qubits)

    return test_flag_grover(
        flag_grover_1,
        input_qubits,
        grover_inputs.hadamard_middle,
        grover_inputs.hadamard_end,
    )


def challenge_grover_2(data: Dict[str, List[float] | List[int]]) -> str:
    try:
        grover_inputs = GroverInput(**data)  # type: ignore
    except ValidationError as e:
        return str(e)
    except Exception as e:
        return str(e)

    input_qubits = Circuit.from_angles(grover_inputs.input_qubits)

    return test_flag_grover(
        flag_grover_2,
        input_qubits,
        grover_inputs.hadamard_middle,
        grover_inputs.hadamard_end,
    )
