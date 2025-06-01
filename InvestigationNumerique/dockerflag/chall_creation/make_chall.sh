#! /bin/bash

CHALL_DIR=git_repos



if [ -z "${CHALL_FLAG}" ]; then
	echo "Building chall but with default flag. To change it, please set variable CHALL_FLAG."
fi

rm -rf $CHALL_DIR
mkdir $CHALL_DIR
cd $CHALL_DIR
git init .
git branch -m main
cp ../files/README.md ./
git add .
git commit -m "Project presentation in README"
cp ../files/app.py ./
git add .
git commit -m "Source code of website"
echo "SECRET=\"404CTF{${CHALL_FLAG:=492f3f38d6b5d3ca859514e250e25ba65935bcdd9f4f40c124b773fe536fee7d}}\"" > ../files/.env
cp ../files/.env ./
git add .
git commit -m "Last commit before week-end !"
rm ./.env
cp -r ../files/static ./
git add .
git commit -m "Add static ressources"
cp ../requirements.txt ./
git add .
git commit -m "Requirements of website"
cp -r ../files/templates ./
git add .
git commit -m "Add HTML website"

ls -d -1 -a .git/* | grep -v objects | grep -v logs  | grep -v refs | xargs rm -rf

cd ../


docker build . --tag dockerflag:latest
docker save dockerflag:latest --output ../dockerflag.tar
