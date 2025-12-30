#!/bin/bash
# Helper script to convert DOS line endings to Unix line endings
# Usage: ./dos2unix.sh filename

dos2unix algorithm1.sh algorithm2.sh 2>/dev/null || sed -i 's/\r$//' algorithm1.sh algorithm2.sh

