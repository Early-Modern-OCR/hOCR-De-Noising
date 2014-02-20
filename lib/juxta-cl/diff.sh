#!/bin/bash
java -jar -server -Xmn512M -Xms1G -Xmx1G -XX:+OptimizeStringConcat juxta-cl.jar -diff "$@"
