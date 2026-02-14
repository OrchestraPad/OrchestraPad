#!/bin/bash
# Debug script to check if delete functionality exists

cd ~/Noten

echo "=== Checking VERSION ==="
cat VERSION

echo -e "\n=== Checking last git commit ==="
git log --oneline -1

echo -e "\n=== Checking if deleteSong function exists ==="
grep -n "function deleteSong" templates/index.html

echo -e "\n=== Checking if delete button exists ==="
grep -n "onclick=\"deleteSong" templates/index.html

echo -e "\n=== Checking if delete icon is defined ==="
grep -n "id=\"icon-delete\"" templates/index.html

echo -e "\n=== Git status ==="
git status
