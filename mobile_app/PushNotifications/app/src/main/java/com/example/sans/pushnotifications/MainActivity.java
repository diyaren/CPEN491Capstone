package com.example.sans.pushnotifications;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import com.pusher.pushnotifications.PushNotifications;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        PushNotifications.start(getApplicationContext(), "105aa624-524f-4fca-84a5-ee1f86872ece");
        PushNotifications.subscribe("prediction");
    }
}
