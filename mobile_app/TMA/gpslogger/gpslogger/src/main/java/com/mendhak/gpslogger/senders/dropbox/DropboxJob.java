/*
 * Copyright (C) 2016 mendhak
 *
 * This file is part of GPSLogger for Android.
 *
 * GPSLogger for Android is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * GPSLogger for Android is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with GPSLogger for Android.  If not, see <http://www.gnu.org/licenses/>.
 */

package com.mendhak.gpslogger.senders.dropbox;




import com.mendhak.gpslogger.common.PreferenceHelper;
import com.mendhak.gpslogger.common.events.UploadEvents;
import com.mendhak.gpslogger.common.slf4j.Logs;
import com.path.android.jobqueue.Job;
import com.path.android.jobqueue.Params;

import org.slf4j.Logger;

import java.io.File;
import java.io.IOException;

import de.greenrobot.event.EventBus;
import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
public class DropboxJob extends Job {


    private static final Logger LOG = Logs.of(DropboxJob.class);
    private static PreferenceHelper preferenceHelper = PreferenceHelper.getInstance();
    String fileName;


    protected DropboxJob(String fileName) {
        super(new Params(1).requireNetwork().persist().addTags(getJobTag(fileName)));

        this.fileName = fileName;
    }

    @Override
    public void onAdded() {
        LOG.debug("Dropbox job added");
    }

    @Override
    public void onRun() throws Throwable {
        File gpsDir = new File(preferenceHelper.getGpsLoggerFolder());
        File gpxFile = new File(gpsDir, fileName);
        String content_type  ="application/json;charset=utf-8";
//        try {
//            LOG.debug("Beginning upload to dropbox...");
//            InputStream inputStream = new FileInputStream(gpxFile);
//            DbxRequestConfig requestConfig = DbxRequestConfig.newBuilder("GPSLogger").build();
//            DbxClientV2 mDbxClient = new DbxClientV2(requestConfig, PreferenceHelper.getInstance().getDropBoxAccessKeyName());
//            mDbxClient.files().uploadBuilder("/" + fileName).withMode(WriteMode.OVERWRITE).uploadAndFinish(inputStream);
//            EventBus.getDefault().post(new UploadEvents.Dropbox().succeeded());
//        } catch (Exception e) {
//            LOG.error("Could not upload to Dropbox" , e);
//            EventBus.getDefault().post(new UploadEvents.Dropbox().failed(e.getMessage(), e));
//        }
        OkHttpClient client = new OkHttpClient();
        RequestBody file_body = RequestBody.create(MediaType.parse(content_type),gpxFile);

        RequestBody request_body = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                // .addFormDataPart("type",content_type)
                .addFormDataPart("log",fileName, file_body)
                .build();
        String newProfileName = preferenceHelper.getCurrentProfileName();
        Request request = new Request.Builder()
                .url("http://128.189.66.131:5000/prediction/"+newProfileName)
                .post(request_body)
                //.post(file_body)
                .build();

        try {
            Response response = client.newCall(request).execute();

            if(!response.isSuccessful()){
                throw new IOException("Error : "+response);
            }

           // progress.dismiss();

        } catch (IOException e) {
            e.printStackTrace();
        }
    }


    @Override
    protected void onCancel() {
    }

    @Override
    protected boolean shouldReRunOnThrowable(Throwable throwable) {
        EventBus.getDefault().post(new UploadEvents.Dropbox().failed("Could not upload to Dropbox", throwable));
        LOG.error("Could not upload to Dropbox", throwable);
        return false;
    }

    public static String getJobTag(String fileName) {
        return "DROPBOX" + fileName;
    }
}
