package net.accedegh.locationupdates;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.EditText;

import java.io.IOException;
import java.net.URL;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

//('/tma/<int:tma_id> POST
public class CreateTMA1 extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_create_tma1);
       // Button newTMAButton = (Button)findViewById(R.id.NewTMAIDButton);

    }
    public void generateNewTMA(View view) throws IOException {
        final OkHttpClient client = new OkHttpClient();
        Log.v("get here", "I'm here ");

        RequestBody body = RequestBody.create(null, new byte[0]);
        EditText number = (EditText)findViewById(R.id.newTMAID);
        String str = number.getText().toString();
        String path = "http://128.189.66.131:5000/tma/"+str;
        URL url = new URL(path);
        final Request request = new Request.Builder()
                .url(url)
                .post(body)
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
                if(mMessage==409) {
                    Intent Intent = new Intent(CreateTMA1.this, PopupWindow.class);
                    startActivity(Intent);
                }
                if(mMessage==201){
                    Intent intent = new Intent(CreateTMA1.this,MarkerDemoActivity.class);
                    startActivity(intent);
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
    }

