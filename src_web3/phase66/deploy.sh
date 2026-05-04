#!/bin/bash
set -e # WHY: Exit immediately if any command fails to prevent partial deployments
echo "Building vulnerable program..." # WHY: Informing user of the vulnerable program build phase
cd src_web3/phase66/vulnerable_program # WHY: Navigating to the vulnerable program directory
anchor build # WHY: Compiling the vulnerable program to verify it builds correctly
echo "Vulnerable program built successfully." # WHY: Confirming vulnerable program compilation
echo "Building secure program..." # WHY: Informing user of the secure program build phase
cd ../secure_program # WHY: Navigating to the secure program directory relative to vulnerable
anchor build # WHY: Compiling the secure program with all fixes applied
echo "Secure program built successfully." # WHY: Confirming secure program compilation
echo "Both programs built. Deploy with: anchor deploy" # WHY: Reminding user of the next deployment step
