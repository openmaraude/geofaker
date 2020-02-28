#!/bin/bash

cmdline=""

# Arguments with values to provide if set
for value_env in \
    WAIT \
    GEOTAXI_ADDR \
    GEOTAXI_PORT;
do
    value=$(eval "echo \${$value_env}")
    test "$value" == "" && continue

    argname=$(echo $value_env | awk '{print tolower($0)}' | sed 's/_/-/g')
    cmdline="$cmdline --$argname $value"
done

exec geofaker $cmdline "$@"
