#!/bin/bash
# Danh sách các images cần pull
images=(
    "tabledevil/kaspersky"
    "ajilaag/clamav-rest"
    "saferwall/gowindefender"
    "malice/sophos"
    "malice/mcafee"
    "malice/fprot"
    "malice/escan"
    "malice/comodo"
    "saferwall/goavira"
    "malice/avg"
    "malice/zoner"
    "malice/drweb"
)
for image in "${images[@]}"; do
    docker pull "$image" &
done
# Đợi tất cả các tiến trình con hoàn thành
wait