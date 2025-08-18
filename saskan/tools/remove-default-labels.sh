for L in enhancement bug question wontfix invalid duplicate good\ first\ issue help\ wanted; do
  gh label delete --repo "$REPO" "$L" -y || true
done
