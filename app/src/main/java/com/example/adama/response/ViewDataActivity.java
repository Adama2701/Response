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

        eatentoday.setText(dbArguments.callFoo()+"");

    }
}
