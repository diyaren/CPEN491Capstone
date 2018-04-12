package net.accedegh.locationupdates;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import java.io.IOException;
import java.net.URL;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

//('/tma/<int:tma_id> POST
public class NotificationConfirm extends AppCompatActivity {
    String driverID;
    String sessionNum;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_notification_confirm);
        driverID = getIntent().getExtras().getString("driverID");
        sessionNum  = getIntent().getExtras().getString("sessionNum");
        TextView textView = (TextView)findViewById(R.id.AnomlyDetail);
        textView.setText("Driver "+ driverID+" in Session "+sessionNum+" had been detected");
        // Button newTMAButton = (Button)findViewById(R.id.NewTMAIDButton);

    }

    public void AgreeEvent(View view) throws IOException {
        final OkHttpClient client = new OkHttpClient();
        Log.v("get here", "I'm here ");
        MediaType mediaType = MediaType.parse("application/json");
        //RequestBody body = RequestBody.create(null, new byte[0]);
        RequestBody body = RequestBody.create(mediaType, "{\n  \"session_num\":"+sessionNum+",\n  \"prediction_confirmation\": "+driverID+"\n}");
        String path = "http://128.189.66.131:5000/prediction/"+driverID;
        URL url = new URL(path);
        final Request request = new Request.Builder()
                .url(url)
                .patch(body)
                .build();
        client.newCall(request);
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                String mMessage = e.getMessage().toString();
                Log.w("failure Response", mMessage);
                call.cancel();
            }

            @Override
            public void onResponse(Call call, Response response)
                    throws IOException {
                Log.v("get here", "I'm here ");
                int mMessage = response.code();
                if(mMessage==200) {
                    Intent Intent = new Intent(NotificationConfirm.this, FalseNotifications.class);
                    startActivity(Intent);
                }

                Log.v("the messages is", "code:"+ mMessage);
                if (response.isSuccessful()) {
                    Log.v("also here", "I'm here ");
                    try {
                        // JSONObject json = new JSONObject(mMessage);
                        //final String serverResponse = json.getString("Your Index");

                    } catch (Exception e) {
                        e.printStackTrace();
                    }

                }
            }

        });




    }

    public void NotAgreeEvent(View view){
        Toast.makeText(getApplicationContext(),
                        ("Thank you for your confirmation.\n Retraining Starts"), Toast.LENGTH_SHORT).show();
            Intent Intent = new Intent (this,FalseNotifications.class);
            startActivity(Intent);
        }

}

