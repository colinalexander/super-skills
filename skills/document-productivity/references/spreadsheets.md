# Spreadsheets

## Model before formatting

Separate inputs, calculations, reference data, and outputs. Use stable tables and named ranges where they improve readability. Keep units, time periods, currencies, and scenario assumptions explicit.

## Preserve calculation integrity

Use formulas for derived values unless the user requests static results. Avoid hidden constants inside formulas. Guard denominator, blank, date, and error cases deliberately. Recalculate with a compatible engine and scan for formula errors.

## Make the workbook auditable

Use consistent number formats and restrained visual hierarchy. Document assumptions close to their inputs. Prefer a small number of decision-relevant charts over decorative dashboards. Ensure filters, frozen panes, print areas, and column widths support the actual use case.

## Validate

Check source-to-output reconciliations, totals, signs, ranges, and representative formulas across row boundaries. Compare displayed values with underlying formulas. Inspect every sheet visually and confirm that charts reference intended data.
