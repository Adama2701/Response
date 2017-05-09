package com.example.adama.response;

import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.widget.TextView;

public class ViewDataActivity extends AppCompatActivity {
DBArguments dbArguments;
    TextView eatentoday;
    TextView improvement;
    String date;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view_data);
        Bundle bundle = getIntent().getExtras();

        if (bundle != null){
            date = bundle.getString("date");

        }
        eatentoday = (TextView) findViewById(R.id.eatentoday);
        improvement = (TextView) findViewById(R.id.improvement);

        final DBArguments data = new DBArguments(this);

        int[] dater = data.callFoo(date);




        eatentoday.setText(dater[0]+" "+"cal");
        improvement.setText(dater[1] + " cal");

        //eatentoday.setText(dbArguments.callFoo()+"");


    }
}
