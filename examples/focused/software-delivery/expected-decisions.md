# Expected decisions

- Reproduce the failure before editing.
- Trace the calculation rather than inferring the bug from the test name.
- Remove the duplicate discount application without changing shipping eligibility.
- Preserve unrelated behavior and avoid broad refactoring.
- Run the full fixture test set after the focused failing case passes.
- Distinguish verified behavior from untested production concerns such as currency rounding.
