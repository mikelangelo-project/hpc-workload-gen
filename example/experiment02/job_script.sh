#!/bin/bash

currDir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)";

if [ ! -e $currDir/inputData ]; then
  echo "Input data dir is missing ?!"
elif [ ! -e $currDir/input_data/testFile.txt ]; then
  echo "Input data dir is empty ?!";
else
  echo "Input data found";
  cat $currDir/input_data/testFile.txt
fi

exit $?;