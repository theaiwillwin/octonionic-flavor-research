# Independent verification: saturated quotient Hessian v1

**FAIL**

- branches independently recomputed: 21
- maximum sorted-spectrum discrepancy: `2.096e-06`
- finite-difference stable branches: 21
- finite-difference isolated branches: 11
- PMNS-evaluable saturated branches: 5
- PMNS-compatible saturated branches: 0
- PMNS-evaluable isolated branches: 0

Method: centered finite differences of the true-SVD first gradient, followed by an independently reconstructed residual-SU(3) quotient.

This independently verifies the 21 unitary-saturated Hessians from the retained stationary branches. It does not turn the finite four-start search into a global no-go theorem.
