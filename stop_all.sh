ps aux | grep phrase_server | grep -v grep | awk '{print $2}'| xargs kill -9
