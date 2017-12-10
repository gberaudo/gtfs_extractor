#!/bin/bash

if [ ! $# -eq 1 ]
then
  echo missing directory
  exit 1
fi

for i in $1/*
do
	sed -i $'1s/^\uFEFF//' $i
done
