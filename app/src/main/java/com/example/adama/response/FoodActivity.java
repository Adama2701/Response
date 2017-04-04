package com.example.adama.response;

import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Spinner;

public class FoodActivity extends AppCompatActivity implements AdapterView.OnItemSelectedListener{

    Spinner month;
    Spinner day;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_food);

        month = (Spinner) findViewById(R.id.month);
        day = (Spinner) findViewById(R.id.day);

        ArrayAdapter adapter1 = ArrayAdapter.createFromResource(this, R.array.month, android.R.layout.simple_spinner_item);
        month.setAdapter(adapter1);
        month.setOnItemSelectedListener(this);


        ArrayAdapter adapter2 = ArrayAdapter.createFromResource(this, R.array.day, android.R.layout.simple_spinner_item);
        day.setAdapter(adapter2);
        day.setOnItemSelectedListener(this);

    }

    @Override
    public void onItemSelected(AdapterView<?> adapterView, View view, int i, long l) {

    }

    @Override
    public void onNothingSelected(AdapterView<?> adapterView) {

    }
}
