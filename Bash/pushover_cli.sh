#!/bin/bash

push_to_mobile() {
    local t="${1:-cli-app}"
    local m="$2"
    local _user="$3"
    local _token="$4"

    [[ "$m" != "" ]] && curl -s \
       --form-string "token=${_token}" \
       --form-string "user=${_user}" \
       --form-string "title=$t" \
       --form-string "message=$m" \
       https://api.pushover.net/1/messages.json
}
