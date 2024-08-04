#!/bin/bash

# Backup the current requirements.txt
cp requirements.txt requirements.txt.bak

# Update requirements.txt with the current installed packages
pip freeze > requirements.txt

# Compare the old and new requirements.txt to find added packages
added_packages=$(comm -13 <(sort requirements.txt.bak) <(sort requirements.txt))

if [ -z "$added_packages" ]; then
    echo "No new packages were added."
else
    echo "The following packages have been added to requirements.txt:"
    echo "$added_packages"
fi

# Clean up the backup file
rm requirements.txt.bak
