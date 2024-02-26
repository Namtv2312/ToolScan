#!/bin/bash
# Run each Docker update command in the background
docker run --name=windows-defender malice/windows-defender update &
docker run --name=comodo malice/comodo update &
docker run --name=escan malice/escan update &
docker run --name=mcafee malice/mcafee update &
docker run --name=avira malice/avira update &
# Wait for all background jobs to finish
docker pull tabledevil/kaspersky:latest &
wait
# Commit the Docker images
docker commit windows-defender malice/windows-defender:update
docker commit comodo malice/comodo:update
docker commit escan malice/escan:update
docker commit mcafee malice/mcafee:update
docker commit avira malice/avira:update
# Remove the containers
docker rm windows-defender
docker rm comodo
docker rm escan
docker rm mcafee
docker rm avira
#Run CLAM_AV_rest
CONTAINER_NAME="clamav-rest"
IMAGE_NAME="ajilaag/clamav-rest"

# Kiểm tra xem container cũ có đang chạy không
if docker ps -a --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
  echo "Dừng container cũ..."
  docker stop $CONTAINER_NAME
  docker rm $CONTAINER_NAME
fi
docker run -p 9000:9000 -p 9443:9443 -itd --name $CONTAINER_NAME $IMAGE_NAME

# Remove dangling images
docker rmi $(docker images -f "dangling=true" -q)
