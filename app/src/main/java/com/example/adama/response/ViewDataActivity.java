package com.example.adama.response;

import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.widget.TextView;

public class ViewDataActivity extends AppCompatActivity {
DBArguments dbArguments;
    TextView eatentoday;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view_data);

        eatentoday = (TextView) findViewById(R.id.eatentoday);

        final DBArguments data = new DBArguments(this);



       // int kat = data.callFoo();
        //System.out.println(kat);

       // eatentoday.setText(kat+""+"cal");

        //eatentoday.setText(dbArguments.callFoo()+"");


    }
}
