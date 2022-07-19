# In place of a README, to remind me what I was doing, here's a brief flow that worked once-upon-a-time

set -e

# Clean up after yourself
trap 'jobs -p | xargs kill' EXIT

STEP_DELIMITER="--------------------------------------"

echo "$STEP_DELIMITER"
if [ -z "$SKIP_SETUP" ]
then
  echo "-- Setup venv, install dependencies"
  python3.8 -m venv env
  source env/bin/activate
  pip install -U -r ./python/requirements.txt

  echo "$STEP_DELIMITER"
  echo "-- Build protobufs"
  SCRIPTS_DIR=$( dirname ${BASH_SOURCE[0]} )
  ${SCRIPTS_DIR}/build_proto.sh
else
  echo "-- Skipping setup"
fi

echo "$STEP_DELIMITER"
echo "-- Start a server"
python ./python/ccfake/kv_server.py &
sleep 5

echo "$STEP_DELIMITER"
echo "-- Register a new worker"
python ./python/ccfake/register_new_executor.py

echo "$STEP_DELIMITER"
echo "-- Test that the new executor has permissions"
python ./python/ccfake/kv_client.py &
sleep 2
curl http://127.0.0.1:8000/app/test_1

echo "$STEP_DELIMITER"
echo "-- Sanity check that we can call multiple times"
python ./python/ccfake/kv_client.py &
sleep 2
curl http://127.0.0.1:8000/app/test_2
python ./python/ccfake/register_new_executor.py
python ./python/ccfake/kv_client.py &
python ./python/ccfake/kv_client.py &
sleep 2
curl http://127.0.0.1:8000/app/test_3
curl http://127.0.0.1:8000/app/test_4
