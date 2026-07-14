"""Independent verifier for the retained E6 heavy sterile-neutrino result.

The verifier re-reads the primary PDF, checks the transcribed benchmark tokens,
and recomputes all masses with Decimal arithmetic rather than NumPy.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
import hashlib
import json
from pathlib import Path
import re

import fitz


getcontext().prec = 50
ROOT = Path(r"D:/Projects/can_o_worms")
INPUT = ROOT / "heavy_sterile_neutrino_benchmark_inputs_v1.json"
RESULT = ROOT / "heavy_sterile_neutrino_spectrum_results_v1.json"
OUTPUT = ROOT / "heavy_sterile_neutrino_independent_verification_v1.json"
PDF = Path(
    r"C:/Users/theai/AppData/Local/hermes/profiles/d-drive-profile/personal/"
    r"e6_pivot_gate/sources/1504.00904.pdf"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compact(text: str) -> str:
    return re.sub(r"\s+", "", text).replace("−", "-").replace("ﬁ", "fi")


def decimal_matrix(scale: Decimal, rows: list[list[float]]) -> list[list[Decimal]]:
    return [[scale * Decimal(str(value)) for value in row] for row in rows]


def physical_diagonal_masses(matrix: list[list[Decimal]]) -> list[Decimal]:
    assert matrix[0][1] == 0 and matrix[1][0] == 0
    return sorted((abs(matrix[0][0]), abs(matrix[1][1])))


def assert_result_matches(
    reported: list[float], expected: list[Decimal], label: str
) -> list[str]:
    checks = []
    for index, (actual, wanted) in enumerate(zip(reported, expected, strict=True)):
        actual_decimal = Decimal(str(actual))
        relative = abs(actual_decimal - wanted) / wanted
        if relative > Decimal("1e-15"):
            raise AssertionError(
                f"{label}[{index}] mismatch: reported={actual_decimal}, expected={wanted}"
            )
        checks.append(f"{label}[{index}] relative_error={relative}")
    return checks


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError("v1 verification output exists; create a new version")

    inputs = json.loads(INPUT.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    if sha256(PDF) != inputs["source"]["pdf_sha256"]:
        raise AssertionError("Primary PDF hash no longer matches the retained provenance")

    document = fitz.open(PDF)
    page_15 = compact(document[14].get_text("text", sort=True))
    page_21 = compact(document[20].get_text("text", sort=True))
    document.close()

    source_checks = {
        "nu_c_in_16": "The16ofSO(10)containstheSMparticles1andtheright-handedneutrinoνc." in page_15,
        "s_is_sterile_SO10_singlet": "TheSO(10)singlet1isdenotedbysissterile" in page_15,
        "nu_c_majorana_entry_f1Y351prime": "f1Y351′" in page_15,
        "s_majorana_entry_f3Y351prime": "f3Y351′" in page_15,
        "fit_point_1_f1": "f1[GeV]4.12×1011-5.52×1012" in page_21,
        "fit_point_1_f3": "f3[GeV]-1.84×10161.38×1016" in page_21,
        "fit_y351_11": "(Y351′)11-0.3710.733" in page_21,
        "fit_y351_22": "(Y351′)220.363-0.287" in page_21,
    }
    failed_source_checks = [name for name, passed in source_checks.items() if not passed]
    if failed_source_checks:
        raise AssertionError(f"Primary-source checks failed: {failed_source_checks}")

    arithmetic_checks: list[str] = []
    independently_computed = {}
    for point_name, point in inputs["benchmark_points"].items():
        y = point["Y351_prime"]
        nu_c_matrix = decimal_matrix(Decimal(str(point["f1_GeV"])), y)
        s_matrix = decimal_matrix(Decimal(str(point["f3_GeV"])), y)
        nu_c_masses = physical_diagonal_masses(nu_c_matrix)
        s_masses = physical_diagonal_masses(s_matrix)

        reported_point = result["points"][point_name]
        arithmetic_checks.extend(
            assert_result_matches(
                reported_point["nu_c_spectrum"]["physical_masses_GeV_sorted"],
                nu_c_masses,
                f"{point_name}.nu_c",
            )
        )
        arithmetic_checks.extend(
            assert_result_matches(
                reported_point["s_spectrum"]["physical_masses_GeV_sorted"],
                s_masses,
                f"{point_name}.s",
            )
        )
        independently_computed[point_name] = {
            "nu_c_physical_masses_GeV": [str(value) for value in nu_c_masses],
            "s_physical_masses_GeV": [str(value) for value in s_masses],
        }

    dimension_check = {
        "claimed_F4_26_lhs": 26,
        "claimed_rhs_16_plus_10_plus_1": sum((16, 10, 1)),
        "equal": 26 == sum((16, 10, 1)),
    }
    if dimension_check["equal"]:
        raise AssertionError("The intentionally tested dimension contradiction disappeared")

    verification = {
        "schema": "heavy-sterile-neutrino-independent-verification/v1",
        "status": "PASS",
        "primary_pdf_sha256": sha256(PDF),
        "input_sha256": sha256(INPUT),
        "result_sha256": sha256(RESULT),
        "source_checks": source_checks,
        "independently_computed": independently_computed,
        "arithmetic_checks": arithmetic_checks,
        "local_F4_26_branching_dimension_check": dimension_check,
        "scope_limit": (
            "The heavy nu_c and s Majorana subblocks are verified. Exact full neutral-fermion "
            "mixing is not verified because the benchmark table omits the needed EW VEV composition."
        ),
    }
    OUTPUT.write_text(json.dumps(verification, indent=2), encoding="utf-8")
    print("PASS")
    print(f"WROTE {OUTPUT}")
    print(f"OUTPUT_SHA256 {sha256(OUTPUT)}")
    for name, values in independently_computed.items():
        print(name, values)
    print("FULL_MIXING_STATUS BLOCKED_BY_MISSING_EW_VEV_COMPOSITION")


if __name__ == "__main__":
    main()
