#!/bin/bash
current_timezone=$(date +%:z)
current_offset=${current_timezone/:/}
# Tính toán giờ theo múi giờ UTC+7
desired_hour=2
desired_minute=30
offset_hours=7
desired_local_hour=$((desired_hour + current_offset -  offset_hours))
if [ $desired_local_hour -le 0 ]; then
    desired_local_hour=$((desired_local_hour + 24))
fi
script_dir="$(cd "$(dirname "$0")" && pwd)"
daily_update_script="$script_dir/daily_update_db.sh"
echo "$desired_minute $desired_local_hour * * * $daily_update_script" >> temp_cron
crontab temp_cron
rm temp_cron

