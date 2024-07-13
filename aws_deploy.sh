# !/bin/bash
# This script will make the connection to AWS EC2 instance using ssh
# and then pull the most up to date code from git and then build the docker container

ssh -A -tt -o StrictHostKeyChecking=no $2 "ssh -i private-ec2-instances.pem $3 '
cd /var/www/makkhimeter/
git fetch --all
git checkout -B $1 origin/$1
./docker_cleanup.sh
docker-compose down -v
docker system prune --all --force
docker stop $(docker ps -q)
docker rm $(docker ps -aq)
docker rmi $(docker images -q)
git pull
export IMAGE_TAG=$4
export SERVER_TYPE=$5
./compose-up.sh
' "
