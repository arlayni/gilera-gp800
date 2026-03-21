"""Safety validation for IAW 5AM ECU map files."""
from .models import MapFile, MapTable, ValidationResult
from .schemas import get_hard_limit


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
