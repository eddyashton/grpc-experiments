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

SERVER_CA=./bl_server_cert.pem

echo "$STEP_DELIMITER"
echo "-- Start a server"
python ./python/ccfake/kv_server.py --ca-out "${SERVER_CA}" &
sleep 2


WORKER_A_CERT=./worker_a_cert.pem
WORKER_A_KEY=./worker_a_privk.pem

echo "$STEP_DELIMITER"
echo "-- Register worker A"
python ./python/ccfake/register_new_executor.py --ca "${SERVER_CA}" --cert "${WORKER_A_CERT}" --key "${WORKER_A_KEY}"

echo "$STEP_DELIMITER"
echo "-- Start worker A"
python ./python/ccfake/bl_logging.py --ca "${SERVER_CA}" --cert "${WORKER_A_CERT}" --key "${WORKER_A_KEY}" &
sleep 1


echo "$STEP_DELIMITER"
echo "-- Test some unsupported endpoints"
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/unsupported
curl http://127.0.0.1:8000/app/no_handler

echo "$STEP_DELIMITER"
echo "-- Test some supported endpoints"
curl http://127.0.0.1:8000/app/log --data-binary '{"id": 42, "msg": "Hello world\n"}'
curl http://127.0.0.1:8000/app/log --data-binary '{"id": 43, "msg": "Saluton mondo\n"}'
curl http://127.0.0.1:8000/app/log -X GET --data-binary '{"id": 42}'
curl http://127.0.0.1:8000/app/log -X GET --data-binary '{"id": 43}'


WORKER_B_CERT=./worker_b_cert.pem
WORKER_B_KEY=./worker_b_privk.pem

echo "$STEP_DELIMITER"
echo "-- Register worker B"
python ./python/ccfake/register_new_executor.py --ca "${SERVER_CA}" --cert "${WORKER_B_CERT}" --key "${WORKER_B_KEY}"

echo "$STEP_DELIMITER"
echo "-- Start worker B"
python ./python/ccfake/bl_logging.py --ca "${SERVER_CA}" --cert "${WORKER_B_CERT}" --key "${WORKER_B_KEY}" &


WORKER_C_CERT=./worker_c_cert.pem
WORKER_C_KEY=./worker_c_privk.pem

echo "$STEP_DELIMITER"
echo "-- Register worker C"
python ./python/ccfake/register_new_executor.py --ca "${SERVER_CA}" --cert "${WORKER_C_CERT}" --key "${WORKER_C_KEY}"

echo "$STEP_DELIMITER"
echo "-- Start worker C"
python ./python/ccfake/bl_logging.py --ca "${SERVER_CA}" --cert "${WORKER_C_CERT}" --key "${WORKER_C_KEY}" &


sleep 1

curl http://127.0.0.1:8000/app/log -X GET --data-binary '{"id": 42}'
curl http://127.0.0.1:8000/app/log -X GET --data-binary '{"id": 43}'
curl http://127.0.0.1:8000/app/log -X GET --data-binary '{"id": 42}'
curl http://127.0.0.1:8000/app/log -X GET --data-binary '{"id": 43}'
curl http://127.0.0.1:8000/app/log -X GET --data-binary '{"id": 42}'
curl http://127.0.0.1:8000/app/log -X GET --data-binary '{"id": 43}'
curl http://127.0.0.1:8000/app/log -X GET --data-binary '{"id": 42}'
curl http://127.0.0.1:8000/app/log -X GET --data-binary '{"id": 43}'
curl http://127.0.0.1:8000/app/log -X GET --data-binary '{"id": 42}'
curl http://127.0.0.1:8000/app/log -X GET --data-binary '{"id": 43}'
curl http://127.0.0.1:8000/app/log -X GET --data-binary '{"id": 42}'
curl http://127.0.0.1:8000/app/log -X GET --data-binary '{"id": 43}'