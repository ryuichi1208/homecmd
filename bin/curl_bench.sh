#!/bin/bash


# Usage
# 
# ./check-speed.sh 'http://example.com/'
# 
# ./check-speed.sh -tsv 'http://example.com/'
#
# ./check-speed.sh -ltsv 'http://example.com/'
# 

if echo "$1" | egrep -q '^-';  then
    case "$1" in
        "-tsv") mode="tsv";;
        "-ltsv") mode="ltsv";;
    esac
    shift;
fi


url="$1"


data=$(curl -s \
 -H 'accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8' \
 -H 'accept-encoding:gzip, deflate, br' \
 -H 'accept-language:en-US,en;q=0.8' \
 -H 'cache-control:no-cache' \
 -H 'pragma:no-cache' \
 -H 'upgrade-insecure-requests:1' \
 -H 'user-agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/61.0.3163.79 Chrome/61.0.3163.79 Safari/537.36' \
 -m 15 \
 -o /dev/null \
 -w 'code:%{http_code} size_download:%{size_download} time_namelookup:%{time_namelookup} time_connect:%{time_connect} time_appconnect:%{time_appconnect} time_pretransfer:%{time_pretransfer} time_starttransfer:%{time_starttransfer} time_total:%{time_total} \n' \
 "$url")

if [[ "$?" != 0 ]];  then # it means prior curl command failed
    echo "curl failed"
    exit 2
fi

size_download=$(echo "$data" | perl -ne 's|^.*size_download:([.0-9]+) .*$|$1|; print;')
msec_time_namelookup=$(echo "$data" | perl -ne 's|^.*time_namelookup:([.0-9]+) .*$|$1|; print ($_ * 1000);')
msec_time_connect=$(echo "$data" | perl -ne 's|^.*time_connect:([.0-9]+) .*$|$1|; print ($_ * 1000);')
msec_time_pretransfer=$(echo "$data" | perl -ne 's|^.*time_pretransfer:([.0-9]+) .*$|$1|; print ($_ * 1000);')
msec_time_starttransfer=$(echo "$data" | perl -ne 's|^.*time_starttransfer:([.0-9]+) .*$|$1|; print ($_ * 1000);')
msec_time_total=$(echo "$data" | perl -ne 's|^.*time_total:([.0-9]+) .*$|$1|; print ($_ * 1000);')

# debug
# echo "$msec_time_namelookup $msec_time_connect $msec_time_pretransfer $msec_time_starttransfer $msec_time_total"

response_size=$size_download
msec_namelookup=$msec_time_namelookup
msec_connect=$(($msec_time_connect - $msec_time_namelookup))
msec_ssl_handshake_overhead=$(($msec_time_pretransfer - $msec_time_connect))
msec_request_to_first_byte=$(($msec_time_starttransfer - $msec_time_pretransfer))
msec_client_transfer_request=$(($msec_connect / 2))
msec_server_generate_response=$(($msec_request_to_first_byte - $msec_connect))
msec_server_transfer_response=$(($msec_time_total - $msec_time_starttransfer + (msec_connect / 2)))
msec_total=$(($msec_namelookup + $msec_connect + $msec_ssl_handshake_overhead + $msec_client_transfer_request + $msec_server_generate_response + $msec_server_transfer_response))


case "$mode" in
    "tsv")
        echo -e "$response_size\t$msec_namelookup\t$msec_connect\t$msec_ssl_handshake_overhead\t$msec_client_transfer_request\t$msec_server_generate_response\t$msec_server_transfer_response\t$msec_total";;
    "ltsv")
        echo -e "response_size:$response_size\tmsec_namelookup:$msec_namelookup\tmsec_connect:$msec_connect\tmsec_ssl_handshake_overhead:$msec_ssl_handshake_overhead\tmsec_client_transfer_request:$msec_client_transfer_request\tmsec_server_generate_response:$msec_server_generate_response\tmsec_server_transfer_response:$msec_server_transfer_response\tmsec_total:$msec_total";;
    *)
        echo "---- curl raw variable values ----"
        echo "$data" | perl -ne 's| |\n|g; s|:|: |g; print;' | column -t
        echo
        echo "---- calculated each phase times ----"
        echo "response_size: $response_size bytes
msec_namelookup: $msec_namelookup msec
msec_connect: $msec_connect  msec
msec_ssl_handshake_overhead: $msec_ssl_handshake_overhead msec
msec_client_transfer_request(estimated): $msec_client_transfer_request msec
msec_server_generate_response(estimated): $msec_server_generate_response msec
msec_server_transfer_response(estimated): $msec_server_transfer_response msec
msec_total: $msec_total msec" | column -t;;
esac
