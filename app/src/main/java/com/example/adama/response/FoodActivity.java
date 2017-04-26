package com.example.adama.response;
//push

import android.content.Intent;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.view.View;
import android.widget.CalendarView;
import android.widget.Spinner;

import java.util.ArrayList;

public class FoodActivity extends AppCompatActivity implements FoodOverview.itemClickCallback{

    Spinner month;
    Spinner day;
    FloatingActionButton plusbutton;
    RecyclerView recyclerView;
    FoodOverview foodOverview;
    ArrayList arrayList1;
    CalendarView calendar;
    ArrayList eventday;

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
        calendar = (CalendarView) findViewById(R.id.calendar);


    }

    @Override
    public void onItemClick(View view, int position) {

    }
}