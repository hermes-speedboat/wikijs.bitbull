#!/bin/bash
# Keep paperless_ops.py beside this executable.
set -Eeuo pipefail
exec python3 "$(dirname -- "$(readlink -f -- "$0")")/paperless_ops.py" upgrade "$@"
