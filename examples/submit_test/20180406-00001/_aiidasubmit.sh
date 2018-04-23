#!/bin/bash
exec > _scheduler-stdout.txt
exec 2> _scheduler-stderr.txt


'./ape' < 'ape.in' > 'ape.out' 
