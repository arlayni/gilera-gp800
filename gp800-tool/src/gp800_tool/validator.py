"""Safety validation for IAW 5AM ECU map files."""
from .models import MapFile, MapTable, ValidationResult
from .schemas import get_hard_limit
from .binary_parser import BinaryDump, IAW5AM_BIN_SIZE


def validate_map_file(map_file: MapFile, safe_ranges: dict) -> list[ValidationResult]:
    """Run all safety checks against a parsed map file.

    Returns a list of ValidationResult objects. Any result with
    severity='BLOCKER' means the map MUST NOT be flashed.
    """
    results: list[ValidationResult] = []

    for name, table in map_file.tables.items():
        name_lower = name.lower()

        # Fuel map checks
        if "fuel" in name_lower:
            results.extend(_check_fuel_map(table, safe_ranges))

        # Ignition map checks
        if "ignition" in name_lower or "timing" in name_lower:
            results.extend(_check_ignition_map(table, safe_ranges))

        # Lambda target checks
        if "lambda" in name_lower:
            results.extend(_check_lambda_map(table, safe_ranges))

    return results


def _check_fuel_map(table: MapTable, ranges: dict) -> list[ValidationResult]:
    results = []

    if table.has_all_zero_row():
        results.append(ValidationResult(
            passed=False,
            check_name="fuel_all_zero_row",
            message=f"BLOCKER: {table.name} contains an all-zero row (no fuel = lean seizure)",
            severity="BLOCKER",
        ))

    if table.has_all_max_row(255):
        results.append(ValidationResult(
            passed=False,
            check_name="fuel_all_max_row",
            message=f"BLOCKER: {table.name} contains an all-255 row (max saturation = hydro-lock)",
            severity="BLOCKER",
        ))

    # Only check injector duration limits when values are in ms (not raw 8-bit map values)
    # Raw 8-bit fuel maps use values 0-255 as scaling factors, not milliseconds
    if table.value_unit == "ms" and table.max_value() <= 20:
        max_dur = get_hard_limit(ranges, "injector_duration", "max")
        if max_dur:
            for r_idx, row in enumerate(table.data):
                for c_idx, val in enumerate(row):
                    if val > max_dur:
                        results.append(ValidationResult(
                            passed=False,
                            check_name="injector_duration_max",
                            message=f"BLOCKER: {table.name} cell [{r_idx},{c_idx}] = {val}ms exceeds max {max_dur}ms",
                            severity="BLOCKER",
                            cell_references=[f"{table.name}[{r_idx},{c_idx}]"],
                        ))

    if not results:
        results.append(ValidationResult(
            passed=True,
            check_name="fuel_map_check",
            message=f"OK: {table.name} passed all fuel safety checks",
        ))

    return results


def _check_ignition_map(table: MapTable, ranges: dict) -> list[ValidationResult]:
    results = []

    max_adv = get_hard_limit(ranges, "ignition_advance", "max")
    min_adv = get_hard_limit(ranges, "ignition_advance", "min")

    for r_idx, row in enumerate(table.data):
        for c_idx, val in enumerate(row):
            if max_adv is not None and val > max_adv:
                results.append(ValidationResult(
                    passed=False,
                    check_name="ignition_advance_max",
                    message=f"BLOCKER: {table.name} cell [{r_idx},{c_idx}] = {val} deg exceeds max {max_adv} deg (detonation risk)",
                    severity="BLOCKER",
                    cell_references=[f"{table.name}[{r_idx},{c_idx}]"],
                ))
            if min_adv is not None and val < min_adv:
                results.append(ValidationResult(
                    passed=False,
                    check_name="ignition_advance_min",
                    message=f"BLOCKER: {table.name} cell [{r_idx},{c_idx}] = {val} deg below min {min_adv} deg (extreme retard)",
                    severity="BLOCKER",
                    cell_references=[f"{table.name}[{r_idx},{c_idx}]"],
                ))

    if not results:
        results.append(ValidationResult(
            passed=True,
            check_name="ignition_map_check",
            message=f"OK: {table.name} passed all ignition safety checks",
        ))

    return results


def _check_lambda_map(table: MapTable, ranges: dict) -> list[ValidationResult]:
    results = []

    min_lambda = get_hard_limit(ranges, "lambda_target", "min")
    max_lambda = get_hard_limit(ranges, "lambda_target", "max")

    for r_idx, row in enumerate(table.data):
        for c_idx, val in enumerate(row):
            if min_lambda is not None and val < min_lambda:
                results.append(ValidationResult(
                    passed=False,
                    check_name="lambda_below_min",
                    message=f"BLOCKER: {table.name} cell [{r_idx},{c_idx}] = {val} lambda below min {min_lambda}",
                    severity="BLOCKER",
                    cell_references=[f"{table.name}[{r_idx},{c_idx}]"],
                ))
            if max_lambda is not None and val > max_lambda:
                results.append(ValidationResult(
                    passed=False,
                    check_name="lambda_above_max",
                    message=f"BLOCKER: {table.name} cell [{r_idx},{c_idx}] = {val} lambda above max {max_lambda}",
                    severity="BLOCKER",
                    cell_references=[f"{table.name}[{r_idx},{c_idx}]"],
                ))

    if not results:
        results.append(ValidationResult(
            passed=True,
            check_name="lambda_map_check",
            message=f"OK: {table.name} passed all lambda safety checks",
        ))

    return results


def validate_binary(dump: BinaryDump, safe_ranges: dict) -> list[ValidationResult]:
    """Run safety checks on a parsed binary dump.

    Checks:
    - File size matches expected IAW 5AM size
    - Named fuel tables: all-zero rows, all-max rows
    - Idle RPM within range
    """
    results: list[ValidationResult] = []

    # File size check
    if dump.file_size != IAW5AM_BIN_SIZE:
        results.append(ValidationResult(
            passed=False,
            check_name="file_size",
            message=f"BLOCKER: File size {dump.file_size} != expected {IAW5AM_BIN_SIZE} bytes",
            severity="BLOCKER",
        ))

    # Check named tables
    for reg in dump.regions:
        if reg.name.startswith("table_"):
            continue  # Skip heuristic tables

        if "fuel" in reg.name:
            # All-zero row check
            for r_idx, row in enumerate(reg.values):
                if all(v == 0 for v in row):
                    results.append(ValidationResult(
                        passed=False,
                        check_name="fuel_all_zero_row",
                        message=f"BLOCKER: {reg.name} row {r_idx} is all-zero (lean seizure risk)",
                        severity="BLOCKER",
                    ))

            # All-max row check (65535 for 16-bit)
            for r_idx, row in enumerate(reg.values):
                if all(v >= 65535 for v in row):
                    results.append(ValidationResult(
                        passed=False,
                        check_name="fuel_all_max_row",
                        message=f"BLOCKER: {reg.name} row {r_idx} is all-max (hydro-lock risk)",
                        severity="BLOCKER",
                    ))

        if reg.name == "idle_rpm_target":
            min_idle = get_hard_limit(safe_ranges, "idle_rpm", "min")
            max_idle = get_hard_limit(safe_ranges, "idle_rpm", "max")
            if min_idle and max_idle:
                for r_idx, row in enumerate(reg.values):
                    for c_idx, val in enumerate(row):
                        if val < min_idle or val > max_idle:
                            results.append(ValidationResult(
                                passed=False,
                                check_name="idle_rpm_range",
                                message=f"WARNING: idle_rpm_target[{r_idx},{c_idx}] = {val} RPM outside [{min_idle}-{max_idle}]",
                                severity="WARNING",
                            ))

    if not any(not r.passed for r in results):
        results.append(ValidationResult(
            passed=True,
            check_name="binary_validation",
            message="All binary safety checks passed",
        ))

    return results
