if [ -d "/path/java" ]; then
    export JAVA_HOME="/path/java"
else
    export JAVA_HOME=$(dirname $(dirname $(which java)))
fi
