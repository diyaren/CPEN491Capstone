package net.accedegh.locationupdates;
/*
 * Copyright (C) 2012 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.drawable.BitmapDrawable;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import android.os.Handler;
import android.os.SystemClock;
import android.support.annotation.ColorInt;
import android.support.annotation.DrawableRes;
import android.support.design.widget.Snackbar;
import android.support.v4.content.res.ResourcesCompat;
import android.support.v4.graphics.drawable.DrawableCompat;
import android.support.v7.app.AppCompatActivity;
import android.text.SpannableString;
import android.text.style.ForegroundColorSpan;
import android.util.Log;
import android.view.View;
import android.view.animation.BounceInterpolator;
import android.view.animation.Interpolator;
import android.widget.CheckBox;
import android.widget.ImageView;
import android.widget.RadioGroup;
import android.widget.RadioGroup.OnCheckedChangeListener;
import android.widget.SeekBar;
import android.widget.SeekBar.OnSeekBarChangeListener;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.GoogleMap.InfoWindowAdapter;
import com.google.android.gms.maps.GoogleMap.OnInfoWindowClickListener;
import com.google.android.gms.maps.GoogleMap.OnInfoWindowCloseListener;
import com.google.android.gms.maps.GoogleMap.OnInfoWindowLongClickListener;
import com.google.android.gms.maps.GoogleMap.OnMarkerClickListener;
import com.google.android.gms.maps.GoogleMap.OnMarkerDragListener;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.BitmapDescriptor;
import com.google.android.gms.maps.model.BitmapDescriptorFactory;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.LatLngBounds;
import com.google.android.gms.maps.model.Marker;
import com.google.android.gms.maps.model.MarkerOptions;
import com.google.firebase.messaging.RemoteMessage;
import com.pusher.pushnotifications.PushNotificationReceivedListener;
import com.pusher.pushnotifications.PushNotifications;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Random;
import java.util.Timer;
import java.util.TimerTask;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

/**
 * This shows how to place markers on a map.
 */
public class MarkerDemoActivity extends AppCompatActivity implements
        OnMarkerClickListener,
        OnInfoWindowClickListener,
        OnMarkerDragListener,
        OnSeekBarChangeListener,
        OnInfoWindowLongClickListener,
        OnInfoWindowCloseListener,
        OnMapAndViewReadyListener.OnGlobalLayoutAndMapReadyListener {


    static LatLng BRISBANE = new LatLng(49.26183805, -123.25502669);

    static  LatLng MELBOURNE = new LatLng(49.2611258, -123.254737);

    static LatLng DARWIN = new LatLng(49.2639792, -123.254737);

    static LatLng SYDNEY = new LatLng(49.26254998, -123.25103513);

    static LatLng ADELAIDE = new LatLng(49.26137201, -123.25486708);

    static LatLng PERTH = new LatLng(49.26137201, -123.254737);

    static LatLng ALICE_SPRINGS = new LatLng(49.26183805, -123.254737);

    /** Demonstrates customizing the info window and/or its contents. */
    class CustomInfoWindowAdapter implements InfoWindowAdapter {

        // These are both viewgroups containing an ImageView with id "badge" and two TextViews with id
        // "title" and "snippet".
        private final View mWindow;

        private final View mContents;


        CustomInfoWindowAdapter() {
            mWindow = getLayoutInflater().inflate(R.layout.custom_info_contents, null);
            mContents = getLayoutInflater().inflate(R.layout.custom_info_contents, null);
        }

        @Override
        public View getInfoWindow(Marker marker) {
            if (mOptions.getCheckedRadioButtonId() != R.id.custom_info_window) {
                // This means that getInfoContents will be called.
                return null;
            }
            render(marker, mWindow);
            return mWindow;
        }

        @Override
        public View getInfoContents(Marker marker) {
            if (mOptions.getCheckedRadioButtonId() != R.id.custom_info_contents) {
                // This means that the default info contents will be used.
                return null;
            }
            render(marker, mContents);
            return mContents;
        }

        private void render(Marker marker, View view) {
            int badge;
            // Use the equals() method on a Marker to check for equals.  Do not use ==.
            if (marker.equals(mBrisbane)) {
                badge = R.mipmap.icon_car;
            } else if (marker.equals(mAdelaide)) {
                badge = R.mipmap.icon_car;
            } else if (marker.equals(mSydney)) {
                badge = R.mipmap.icon_car;
            } else if (marker.equals(mMelbourne)) {
                badge = R.mipmap.icon_car;
            } else if (marker.equals(mPerth)) {
                badge = R.mipmap.icon_car;
            } else if (marker.equals(mDarwin1)) {
                badge = R.mipmap.icon_car;
            } else if (marker.equals(mDarwin2)) {
                badge = R.mipmap.icon_car;
            } else if (marker.equals(mDarwin3)) {
                badge = R.mipmap.icon_car;
            } else if (marker.equals(mDarwin4)) {
                badge = R.mipmap.icon_car;
            } else {
                // Passing 0 to setImageResource will clear the image view.
                badge = 0;
            }
            ((ImageView) view.findViewById(R.id.badge)).setImageResource(badge);

            String title = marker.getTitle();
            TextView titleUi = ((TextView) view.findViewById(R.id.title));
            if (title != null) {
                // Spannable string allows us to edit the formatting of the text.
                SpannableString titleText = new SpannableString(title);
                titleText.setSpan(new ForegroundColorSpan(Color.RED), 0, titleText.length(), 0);
                titleUi.setText(titleText);
            } else {
                titleUi.setText("");
            }

            String snippet = marker.getSnippet();
            TextView snippetUi = ((TextView) view.findViewById(R.id.snippet));
            if (snippet != null && snippet.length() > 12) {
                SpannableString snippetText = new SpannableString(snippet);
                snippetText.setSpan(new ForegroundColorSpan(Color.MAGENTA), 0, 10, 0);
                snippetText.setSpan(new ForegroundColorSpan(Color.BLUE), 12, snippet.length(), 0);
                snippetUi.setText(snippetText);
            } else {
                snippetUi.setText("");
            }
        }
    }

    private GoogleMap mMap;

    private Marker mPerth;

    private Marker mSydney;

    private Marker mBrisbane;

    private Marker mAdelaide;

    private Marker mMelbourne;

    private Marker mDarwin1;
    private Marker mDarwin2;
    private Marker mDarwin3;
    private Marker mDarwin4;


    /**
     * Keeps track of the last selected marker (though it may no longer be selected).  This is
     * useful for refreshing the info window.
     */
    private Marker mLastSelectedMarker;

    private final List<Marker> mMarkerRainbow = new ArrayList<Marker>();

    private TextView mTopText;

    private SeekBar mRotationBar;

    private CheckBox mFlatBox;

    private RadioGroup mOptions;

    private final Random mRandom = new Random();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_marker_demo);
//        try {
//            getTMACoor();
//        } catch (IOException e) {
//            e.printStackTrace();
//        }


        ALICE_SPRINGS = new LatLng(49.26183805, -123.254737);

        //mTopText = (TextView) findViewById(R.id.top_text);

        //mRotationBar = (SeekBar) findViewById(R.id.rotationSeekBar);
        //mRotationBar.setMax(360);
        //mRotationBar.setOnSeekBarChangeListener(this);

        //mFlatBox = (CheckBox) findViewById(R.id.flat);

        mOptions = (RadioGroup) findViewById(R.id.custom_info_window_options);
        mOptions.setOnCheckedChangeListener(new OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(RadioGroup group, int checkedId) {
                if (mLastSelectedMarker != null && mLastSelectedMarker.isInfoWindowShown()) {
                    // Refresh the info window when the info window's content has changed.
                    mLastSelectedMarker.showInfoWindow();
                }
            }
        });

        SupportMapFragment mapFragment =
                (SupportMapFragment) getSupportFragmentManager().findFragmentById(R.id.map);
        new OnMapAndViewReadyListener(mapFragment, this);

        PushNotifications.start(getApplicationContext(), "105aa624-524f-4fca-84a5-ee1f86872ece");
        PushNotifications.subscribe("prediction");

        PushNotifications.setOnMessageReceivedListener(new PushNotificationReceivedListener() {
            @Override
            public void onMessageReceived(final RemoteMessage remoteMessage) {
                if (remoteMessage.getNotification() != null) {
                    String title = remoteMessage.getNotification().getTitle();
                    String message = remoteMessage.getNotification().getBody();
                    Snackbar mySnackbar = Snackbar.make(findViewById(R.id.map),title+ ": " + message,10000);
                    mySnackbar.show();
                }
            }
        });


    }


    @Override
    public void onMapReady(GoogleMap map) throws IOException {
        mMap = map;

        // Hide the zoom controls as the button panel will cover it.
        mMap.getUiSettings().setZoomControlsEnabled(false);

        // Add lots of markers to the map.
        addMarkersToMap();

        // Setting an info window adapter allows us to change the both the contents and look of the
        // info window.
        mMap.setInfoWindowAdapter(new CustomInfoWindowAdapter());

        // Set listeners for marker events.  See the bottom of this class for their behavior.
        mMap.setOnMarkerClickListener(this);
        mMap.setOnInfoWindowClickListener(this);
        mMap.setOnMarkerDragListener(this);
        mMap.setOnInfoWindowCloseListener(this);
        mMap.setOnInfoWindowLongClickListener(this);

        // Override the default content description on the view, for accessibility mode.
        // Ideally this string would be localised.
        mMap.setContentDescription("Map with lots of markers.");

        LatLngBounds bounds = new LatLngBounds.Builder()
                .include(PERTH)
                .include(SYDNEY)
                .include(ADELAIDE)
                .include(BRISBANE)
                .include(MELBOURNE)
                .include(DARWIN)
                .build();
        mMap.moveCamera(CameraUpdateFactory.newLatLngBounds(bounds, 50));
    }

    public double getRandomx(){
        double xmin = 49.264133;
        double xmax =49.261134;


        Random r = new Random();
        double rangex = xmin +(xmax-xmin)*r.nextDouble();

        return rangex;
    }
    public double getRandomy(){
        double ymin = -123.256322;
        double ymax = -123.2543424;

        Random y = new Random();
        double rangey = ymin +(ymax-ymin)*y.nextDouble();

        return rangey;
    }


    public void addMarkersToMap() throws IOException {

        int height = 150;
        int width = 150;
        BitmapDrawable bitmapdraw1 = (BitmapDrawable)getResources().getDrawable(R.drawable.blue);
        Bitmap a = bitmapdraw1.getBitmap();
        Bitmap smallMarker1 = Bitmap.createScaledBitmap(a,width,height,false);

        BitmapDrawable bitmapdraw2 = (BitmapDrawable)getResources().getDrawable(R.drawable.green);
        Bitmap b = bitmapdraw2.getBitmap();
        Bitmap smallMarker2 = Bitmap.createScaledBitmap(b,width,height,false);

        BitmapDrawable bitmapdraw3 = (BitmapDrawable)getResources().getDrawable(R.drawable.gray);
        Bitmap c = bitmapdraw3.getBitmap();
        Bitmap smallMarker3 = Bitmap.createScaledBitmap(c,width,height,false);

        BitmapDrawable bitmapdraw4 = (BitmapDrawable)getResources().getDrawable(R.drawable.red);
        Bitmap d = bitmapdraw4.getBitmap();
        Bitmap smallMarker4 = Bitmap.createScaledBitmap(d,width,height,false);

        BitmapDrawable bitmapdraw5 = (BitmapDrawable)getResources().getDrawable(R.drawable.orange);
        Bitmap e = bitmapdraw5.getBitmap();
        Bitmap smallMarker5 = Bitmap.createScaledBitmap(e,width,height,false);




        LatLng TMA5 = new LatLng(getRandomx(),getRandomy());
        mBrisbane = mMap.addMarker(new MarkerOptions()
                .position(TMA5)
                .title("TMA5")
                .icon(BitmapDescriptorFactory.fromBitmap(smallMarker1)));
        mBrisbane.showInfoWindow();

        // Uses a custom icon with the info window popping out of the center of the icon.
        LatLng TMA4 = new LatLng(getRandomx(),getRandomy());
        mSydney = mMap.addMarker(new MarkerOptions()
                .position(TMA4)
                .title("TMA4")
                .icon(BitmapDescriptorFactory.fromBitmap(smallMarker2)));
       // mSydney.showInfoWindow();

        // Creates a draggable marker. Long press to drag.
        LatLng TMA1 = new LatLng(getRandomx(),getRandomy());
        mMelbourne = mMap.addMarker(new MarkerOptions()
                .position(TMA1)
                .title("TMA1")
                .draggable(true)
                .icon(BitmapDescriptorFactory.fromBitmap(smallMarker3)));

//        mMelbourne.showInfoWindow();
        // A few more markers for good measure.
        LatLng TMA2 = new LatLng(getRandomx(),getRandomy());
        mPerth = mMap.addMarker(new MarkerOptions()
                .position(TMA2)
                .title("TMA2")
                .icon(BitmapDescriptorFactory.fromBitmap(smallMarker4)));
//        mPerth.showInfoWindow();


        LatLng TMA3 = new LatLng(getRandomx(),getRandomy());
        mAdelaide = mMap.addMarker(new MarkerOptions()
                .position(TMA3)
                .title("TMA3")
                .icon(BitmapDescriptorFactory.fromBitmap(smallMarker5)));
  //      mAdelaide.showInfoWindow();

    }
//
//    int height = 150;
//    int width = 150;
//    BitmapDrawable bitmapdraw = (BitmapDrawable)getResources().getDrawable(R.mipmap.car_logo);
//    Bitmap b = bitmapdraw.getBitmap();
//    Bitmap smallMarker = Bitmap.createScaledBitmap(b,width,height,false);



    public void updateMarkersToMap() throws IOException {
        getTMACoor();

        int height = 150;
        int width = 150;
        BitmapDrawable bitmapdraw1 = (BitmapDrawable) getResources().getDrawable(R.drawable.blue);
        Bitmap a = bitmapdraw1.getBitmap();
        Bitmap smallMarker1 = Bitmap.createScaledBitmap(a, width, height, false);

        BitmapDrawable bitmapdraw2 = (BitmapDrawable) getResources().getDrawable(R.drawable.green);
        Bitmap b = bitmapdraw2.getBitmap();
        Bitmap smallMarker2 = Bitmap.createScaledBitmap(b, width, height, false);

        BitmapDrawable bitmapdraw3 = (BitmapDrawable) getResources().getDrawable(R.drawable.gray);
        Bitmap c = bitmapdraw3.getBitmap();
        Bitmap smallMarker3 = Bitmap.createScaledBitmap(c, width, height, false);

        BitmapDrawable bitmapdraw4 = (BitmapDrawable) getResources().getDrawable(R.drawable.red);
        Bitmap d = bitmapdraw4.getBitmap();
        Bitmap smallMarker4 = Bitmap.createScaledBitmap(d, width, height, false);

        BitmapDrawable bitmapdraw5 = (BitmapDrawable) getResources().getDrawable(R.drawable.orange);
        Bitmap e = bitmapdraw5.getBitmap();
        Bitmap smallMarker5 = Bitmap.createScaledBitmap(e, width, height, false);


        while (TMACoor.size() < 5) {

        }
        //int i = 0;
        List<LatLng> points = new ArrayList<LatLng>();
        for (String key : TMACoor.keySet()) {
            // i++;
            // String TMA = "TMA"+i;
            double x = Double.parseDouble(TMACoor.get(key));
            double y = Double.parseDouble(key);
            points.add(new LatLng(x, y));
        }

        // LatLng TMA5 = new LatLng(getRandomx(),getRandomy());
        mBrisbane = mMap.addMarker(new MarkerOptions()
                .position(points.get(0))
                .title("TMA5")
                .icon(BitmapDescriptorFactory.fromBitmap(smallMarker1)));
        mBrisbane.showInfoWindow();

        // Uses a custom icon with the info window popping out of the center of the icon.
        LatLng TMA4 = new LatLng(getRandomx(), getRandomy());
        mSydney = mMap.addMarker(new MarkerOptions()
                .position(points.get(1))
                .title("TMA4")
                .icon(BitmapDescriptorFactory.fromBitmap(smallMarker2)));
        // mSydney.showInfoWindow();

        // Creates a draggable marker. Long press to drag.
        LatLng TMA1 = new LatLng(getRandomx(), getRandomy());
        mMelbourne = mMap.addMarker(new MarkerOptions()
                .position(points.get(2))
                .title("TMA1")
                .draggable(true)
                .icon(BitmapDescriptorFactory.fromBitmap(smallMarker3)));

//        mMelbourne.showInfoWindow();
        // A few more markers for good measure.
        LatLng TMA2 = new LatLng(getRandomx(), getRandomy());
        mPerth = mMap.addMarker(new MarkerOptions()
                .position(points.get(3))
                .title("TMA2")
                .icon(BitmapDescriptorFactory.fromBitmap(smallMarker4)));
//        mPerth.showInfoWindow();


        LatLng TMA3 = new LatLng(getRandomx(), getRandomy());
        mAdelaide = mMap.addMarker(new MarkerOptions()
                .position(points.get(4))
                .title("TMA3")
                .icon(BitmapDescriptorFactory.fromBitmap(smallMarker5)));
        //      mAdelaide.showInfoWindow();

        LatLngBounds bounds = new LatLngBounds.Builder()
                .include(points.get(0))
                .include(points.get(1))
                .include(points.get(2))
                .include(points.get(3))
                .include(points.get(4))
                .build();
        mMap.moveCamera(CameraUpdateFactory.newLatLngBounds(bounds, 100));



    }




    /**
     * Demonstrates converting a {@link Drawable} to a {@link BitmapDescriptor},
     * for use as a marker icon.
     */
    private BitmapDescriptor vectorToBitmap(@DrawableRes int id, @ColorInt int color) {
        Drawable vectorDrawable = ResourcesCompat.getDrawable(getResources(), id, null);
        Bitmap bitmap = Bitmap.createBitmap(vectorDrawable.getIntrinsicWidth(),
                vectorDrawable.getIntrinsicHeight(), Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(bitmap);
        vectorDrawable.setBounds(0, 0, canvas.getWidth(), canvas.getHeight());
        DrawableCompat.setTint(vectorDrawable, color);
        vectorDrawable.draw(canvas);
        return BitmapDescriptorFactory.fromBitmap(bitmap);
    }

    private boolean checkReady() {
        if (mMap == null) {
            Toast.makeText(this, "map not ready",Toast.LENGTH_SHORT).show();
            return false;
        }
        return true;
    }

    /** Called when the Clear button is clicked. */
    public void onClearMap(View view) {
        if (!checkReady()) {
            return;
        }
        mMap.clear();
    }

    /** Called when the Reset button is clicked. */
    public void onResetMap(View view) throws IOException {
        if (!checkReady()) {
            return;
        }
        // Clear the map because we don't want duplicates of the markers.
//   mMap.clear();
//        updateMarkersToMap();
        timerAsync.schedule(timerTaskAsync, 0, 5000);

    }

    /** Called when the Reset button is clicked. */
    public void onToggleFlat(View view) {
        if (!checkReady()) {
            return;
        }
        boolean flat = mFlatBox.isChecked();
        for (Marker marker : mMarkerRainbow) {
            marker.setFlat(flat);
        }
    }

    @Override
    public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        if (!checkReady()) {
            return;
        }
        float rotation = seekBar.getProgress();
        for (Marker marker : mMarkerRainbow) {
            marker.setRotation(rotation);
        }
    }

    @Override
    public void onStartTrackingTouch(SeekBar seekBar) {
        // Do nothing.
    }

    @Override
    public void onStopTrackingTouch(SeekBar seekBar) {
        // Do nothing.
    }

    //
    // Marker related listeners.
    //

    @Override
    public boolean onMarkerClick(final Marker marker) {
        if (marker.equals(mPerth)) {
            // This causes the marker at Perth to bounce into position when it is clicked.
            final Handler handler = new Handler();
            final long start = SystemClock.uptimeMillis();
            final long duration = 1500;

            final Interpolator interpolator = new BounceInterpolator();

            handler.post(new Runnable() {
                @Override
                public void run() {
                    long elapsed = SystemClock.uptimeMillis() - start;
                    float t = Math.max(
                            1 - interpolator.getInterpolation((float) elapsed / duration), 0);
                    marker.setAnchor(0.5f, 1.0f + 2 * t);

                    if (t > 0.0) {
                        // Post again 16ms later.
                        handler.postDelayed(this, 16);
                    }
                }
            });
        }
//        } else if (marker.equals(mAdelaide)) {
//            // This causes the marker at Adelaide to change color and alpha.
//            marker.setIcon(BitmapDescriptorFactory.defaultMarker(mRandom.nextFloat() * 360));
//            marker.setAlpha(mRandom.nextFloat());
//        }

        // Markers have a z-index that is settable and gettable.
        float zIndex = marker.getZIndex() + 1.0f;
        marker.setZIndex(zIndex);
        Toast.makeText(this, marker.getTitle() + " z-index set to " + zIndex,
                Toast.LENGTH_SHORT).show();

        mLastSelectedMarker = marker;
        // We return false to indicate that we have not consumed the event and that we wish
        // for the default behavior to occur (which is for the camera to move such that the
        // marker is centered and for the marker's info window to open, if it has one).
        return false;
    }

    @Override
    public void onInfoWindowClick(Marker marker) {
        Toast.makeText(this, "Click Info Window", Toast.LENGTH_SHORT).show();
    }

    @Override
    public void onInfoWindowClose(Marker marker) {
        //Toast.makeText(this, "Close Info Window", Toast.LENGTH_SHORT).show();
    }

    @Override
    public void onInfoWindowLongClick(Marker marker) {
        Toast.makeText(this, "Info Window long click", Toast.LENGTH_SHORT).show();
    }

    @Override
    public void onMarkerDragStart(Marker marker) {
        mTopText.setText("onMarkerDragStart");
    }

    @Override
    public void onMarkerDragEnd(Marker marker) {
        mTopText.setText("onMarkerDragEnd");
    }

    @Override
    public void onMarkerDrag(Marker marker) {
        mTopText.setText("onMarkerDrag.  Current Position: " + marker.getPosition());
    }

    public void getTMACoor() throws IOException {

        final OkHttpClient client = new OkHttpClient();
        Log.v("get here", "I'm here ");

        //RequestBody body = RequestBody.create(null, new byte[0]);
        final Request request = new Request.Builder()
                .url("http://128.189.66.131:5000/tma")
                .get()
                .build();

        client.newCall(request);
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                //String mMessage = e.getMessage().toString();
                //Log.w("failure Response", mMessage);
                //call.cancel();
            }

            @Override
            public void onResponse(Call call, Response response)
                    throws IOException {
                Log.v("get here", "I'm here ");
                // String mMessage = response.body().string().toString();
                try {
                    JSONObject json = new JSONObject(response.body().string());
                    Log.v("the messages is", "print" + json);
                    JSONObject dataObject = json.getJSONObject("data");
                    Log.v("the messages is", "print" + dataObject);
                    JSONArray tmas = dataObject.getJSONArray("tmas");
                    //Log.v("the messages is", "print"+falsePredictionsArray);
                    for (int i = 0; i < 5; i++) {
                        JSONObject notifications = tmas.getJSONObject(i);
                        Log.v("the messages!!!!!! is", "print" + notifications);
                        String x = notifications.optString("xCoord");
                        String y = notifications.optString("yCoord");
                        CMACoorMap(x, y);
                        Log.v("message","get here"+TMACoor);

                    }

                } catch (JSONException e) {
                    e.printStackTrace();
                }
                if (response.isSuccessful()) {
                    Log.v("also here", "I'm here ");
                    try {
                    } catch (Exception e) {
                        e.printStackTrace();
                    }

                }

            }

        });

    }

    HashMap<String, String> TMACoor = new HashMap<String, String>();
    public HashMap<String, String> CMACoorMap(String x, String y){
        TMACoor.put(x, y);

        return TMACoor;
    }


    Timer timerAsync = new Timer();
    TimerTask timerTaskAsync = new TimerTask() {
        @Override
        public void run() {
            runOnUiThread(new Runnable() {
                @Override public void run() {
                   mMap.clear();
                    try {
                        updateMarkersToMap();
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            });
        }
    };


//    @Override
//    protected void onPause(){
//        handler.removeCallbacks(runnable);
//        super.onPause();
//    }



    public void Prediction(View view){
        Intent Intent = new Intent (this,FalseNotifications.class);
        startActivity(Intent);
    }
    public void CreateTMA(View view){
        Intent Intent = new Intent (this, CreateTMA1.class);
        startActivity(Intent);
    }

}
