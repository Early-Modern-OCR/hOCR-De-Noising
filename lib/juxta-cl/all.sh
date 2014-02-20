#!/bin/bash
echo -n 'JUXTA         : '
java -jar -server -Xmn512M -Xms1G -Xmx1G -XX:+OptimizeStringConcat juxta-cl.jar -diff "$@" -algorithm juxta

echo -n 'LEVENSHTEIN   : '
java -jar -server -Xmn512M -Xms1G -Xmx1G -XX:+OptimizeStringConcat juxta-cl.jar -diff "$@" -algorithm levenshtein

echo -n 'JARO WINKLER  : '
java -jar -server -Xmn512M -Xms1G -Xmx1G -XX:+OptimizeStringConcat juxta-cl.jar -diff "$@" -algorithm jaro_winkler
