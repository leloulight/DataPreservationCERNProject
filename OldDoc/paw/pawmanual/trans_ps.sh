#!/bin/sh
: little script to eliminate the HIGZ translate
for i in $*
do
    if [ -f $i ]; then    
	echo  Treating file $i
	sed -e '/^gsave /{
           s/ 100 100 / 00 00 /
	   }' $i > /tmp/sed_$i
	if [ -s /tmp/sed_$i ]; then
		mv /tmp/sed_$i $i
	fi
    else
 	echo  file $i is non standard
    fi
done
