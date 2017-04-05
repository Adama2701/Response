package com.example.adama.response;

import android.content.Intent;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Spinner;

public class FoodActivity extends AppCompatActivity implements AdapterView.OnItemSelectedListener{

    Spinner month;
    Spinner day;
    FloatingActionButton plusbutton;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_food);

        plusbutton = (FloatingActionButton) findViewById(R.id.plusbutton);
        plusbutton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent jud = new Intent(getApplicationContext(), PlusButtonActivity.class);
                startActivity(jud);
            }
        });

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