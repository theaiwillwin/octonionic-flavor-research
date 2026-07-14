set -e
for f in OCTONIONIC_MASS_HIERARCHY_WITHOUT_SPECTRAL_RIGIDITY.md octonionic_nonhollow_operator_gate.py octonionic_nonhollow_operator_gate_results.json octonion_g2_kernel.py; do
  if [ -e "/d/Projects/can_o_worms/$f" ]; then
    printf 'PRESERVED_EXISTING=%s\n' "$f"
  else
    cp -p "/d/Projects/ToE_21st_June_NEWEST/$f" "/d/Projects/can_o_worms/$f"
    printf 'COPIED_WITHOUT_DELETING_SOURCE=%s\n' "$f"
  fi
done
sha256sum /d/Projects/can_o_worms/OCTONIONIC_MASS_HIERARCHY_WITHOUT_SPECTRAL_RIGIDITY.md /d/Projects/can_o_worms/octonionic_nonhollow_operator_gate.py /d/Projects/can_o_worms/octonionic_nonhollow_operator_gate_results.json /d/Projects/can_o_worms/octonion_g2_kernel.py
printf 'SOURCE_FILES_RETAINED='; if [ -e /d/Projects/ToE_21st_June_NEWEST/octonionic_nonhollow_operator_gate.py ]; then printf 'YES\n'; else printf 'NO\n'; exit 1; fi
