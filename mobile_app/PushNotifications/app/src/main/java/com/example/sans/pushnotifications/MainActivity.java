package com.example.sans.pushnotifications;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;


import com.google.firebase.messaging.RemoteMessage;
import com.pusher.pushnotifications.PushNotificationReceivedListener;
import com.pusher.pushnotifications.PushNotifications;

public class MainActivity extends AppCompatActivity {

    private static final String TAG = "MainActivity";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        PushNotifications.start(getApplicationContext(), "105aa624-524f-4fca-84a5-ee1f86872ece");
        PushNotifications.subscribe("prediction");

        Intent intent = getIntent();
        String tma = intent.getStringExtra("tma");
        String session = intent.getStringExtra("session");

        TextView textView = findViewById(R.id.textView);
        textView.setText(tma);

        PushNotifications.setOnMessageReceivedListener(new PushNotificationReceivedListener() {
            @Override
            public void onMessageReceived(final RemoteMessage remoteMessage){
                if (remoteMessage.getData().size() > 0) {
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            TextView textView2 = findViewById(R.id.textView);
                            textView2.setText(remoteMessage.getData().get("tma"));
                        }
                    });

                }
            }
        });


        /*
        Bundle bundle = intent.getExtras();
        if (bundle != null) {
            for (String key : bundle.keySet()) {
                Object value = bundle.get(key);
                Log.d(TAG, key);
                Log.d(TAG, value.toString());
            }
        }*/


    }
}
