package com.example.adama.response;
//push

import android.content.Intent;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Spinner;

import java.util.ArrayList;

public class FoodActivity extends AppCompatActivity implements AdapterView.OnItemSelectedListener, FoodOverview.itemClickCallback{

    Spinner month;
    Spinner day;
    FloatingActionButton plusbutton;
    RecyclerView recyclerView;
    FoodOverview foodOverview;
    ArrayList arrayList1;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_food);
        DBArguments data = new DBArguments(this);

        foodOverview = new FoodOverview(data.getallfoods(), this);
        System.out.println("Hej");

        foodOverview.setitemClickCallback(this);
        recyclerView = (RecyclerView) findViewById(R.id.recycleview);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        recyclerView.setAdapter(foodOverview);

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

    @Override
    public void onItemClick(View view, int position) {

    }
}