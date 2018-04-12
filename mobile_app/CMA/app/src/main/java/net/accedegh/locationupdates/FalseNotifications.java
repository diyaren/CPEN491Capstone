package net.accedegh.locationupdates;


import android.app.ListActivity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;


public class FalseNotifications extends ListActivity {
    List<Map<String,String>> notificationsList = new ArrayList<Map<String,String>>();
    String[] arr;
    //String[]arr = new String[10];
private static int driverid;
private static int sessionNum;
String  passString;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        arr = new String[]{"", "", ""};
        try {
            getFalseNotification();
        } catch (IOException e) {
            e.printStackTrace();
        }

        Log.v("adapter here","print" + arr);

        setListAdapter(new ArrayAdapter<String>(this,R.layout.activity_false_notifications,arr));


        ListView listView = getListView();
        listView.setTextFilterEnabled(true);

        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            public void onItemClick(AdapterView<?> parent, View view,
                                    int position, long id) {
                // When clicked, show a toast with the TextView text
//                Toast.makeText(getApplicationContext(),
//                        ((TextView) view).getText(), Toast.LENGTH_SHORT).show();
                List<String> numbers = new ArrayList<String>();
                Intent intent  = new Intent(getBaseContext(),NotificationConfirm.class);
                Pattern p = Pattern.compile("-?\\d+");
                Matcher m = p.matcher(((TextView)view).getText());
                while(m.find()){
                    numbers.add(m.group());
                }
                intent.putExtra("driverID",numbers.get(0));
                intent.putExtra("sessionNum",numbers.get(1));
                Log.v("print driver","driver"+ driverid);


                startActivity(intent);

            }
        });
    }




    public void getFalseNotification() throws IOException {

        final OkHttpClient client = new OkHttpClient();
        Log.v("get here", "I'm here ");

        RequestBody body = RequestBody.create(null, new byte[0]);
        final Request request = new Request.Builder()
                .url("http://128.189.66.131:5000/prediction/false")
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
                    Log.v("the messages is", "print"+json);
                    JSONObject dataObject =json.getJSONObject("data");
                    Log.v("the messages is", "print"+dataObject);
                    JSONArray falsePredictionsArray =dataObject.getJSONArray("false_predictions");
                    //Log.v("the messages is", "print"+falsePredictionsArray);
                    for(int i = 0;i < falsePredictionsArray.length();i++){
                        JSONObject notifications = falsePredictionsArray.getJSONObject(i);
                        Log.v("the messages!!!!!! is", "print"+notifications);
                        driverid = notifications.optInt("driverID");
                        sessionNum =notifications.optInt("sessionNum");
                        String Time = notifications.optString("time");
                        String outPut1 = "driver"+ driverid;
                        String outPut2 = " in session "+ sessionNum;
                        String outPut3 = " has been detected suspicious behavior at "+Time;
                        arr[i]=outPut1+outPut2+outPut3;
                        passString  = arr[i];
                        notificationsList.add(createNotificationList("Alert:",outPut1+outPut2+outPut3));
                        while(arr==null){

                        }
                        Log.v("print notification","notification"+notificationsList);

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


    private HashMap<String, String>createNotificationList(String driverID ,String time){
        HashMap<String, String> numofNotifications = new HashMap<String, String>();
        numofNotifications.put(driverID, time);
        return numofNotifications;
    }

}