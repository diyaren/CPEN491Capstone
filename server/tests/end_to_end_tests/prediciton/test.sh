# End-to-end test to test prediciton with a model worker.
# Run the test with a fresh db, we'll generate and upload logs for two
# driver_ids, then upload the incorrect log to make the model detect an anomaly
# and send a push notification.

# create .geojson's
echo "Generating driving data for driver 1 and driver 2"
python generate_geojson.py

# upload the corresponding driver's logs
read -n 1 -s -p "$(echo -e 'Press any key to upload driver 1 log >')"
curl -i -X POST -H "content-type: multipart/form-data" -F "log=@./super_biased_driver1.geojson" 0.0.0.0:5000/prediction/1

read -n 1 -s -p "$(echo -e '\nPress any key to upload driver 2 log >')"
curl -i -X POST -H "content-type: multipart/form-data" -F "log=@./super_biased_driver2.geojson" 0.0.0.0:5000/prediction/2

read -n 1 -s -p "$(echo -e '\nPress any key to upload driver 1 log >')"
curl -i -X POST -H "content-type: multipart/form-data" -F "log=@./super_biased_driver1.geojson" 0.0.0.0:5000/prediction/1

read -n 1 -s -p "$(echo -e '\nPress any key to upload driver 2 log >')"
curl -i -X POST -H "content-type: multipart/form-data" -F "log=@./super_biased_driver2.geojson" 0.0.0.0:5000/prediction/2

# upload the incorrect logs
read -n 1 -s -p "$(echo -e '\nPress any key to upload driver 1s log as driver 2, should trigger an anomaly >')"
curl -i -X POST -H "content-type: multipart/form-data" -F "log=@./super_biased_driver1.geojson" 0.0.0.0:5000/prediction/2

read -n 1 -s -p "$(echo -e '\nPress any key to upload driver 2s log as driver 1, should trigger an anomaly >')"
curl -i -X POST -H "content-type: multipart/form-data" -F "log=@./super_biased_driver2.geojson" 0.0.0.0:5000/prediction/1
