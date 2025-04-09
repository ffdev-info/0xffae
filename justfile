# CLI runners

# help
help:
 @echo "Command line helpers for this project.\n"
 @just -l

# Run all pre-commit checks
pre-commit:
   pre-commit run --all-files

# Run the Python http server
serve:
   python -m http.server
