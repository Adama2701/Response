package com.example.adama.response;
//push

import android.content.Intent;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.design.widget.FloatingActionButton;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.view.View;
import android.widget.Button;
import android.widget.CalendarView;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;

public class FoodActivity extends AppCompatActivity implements FoodOverview.itemClickCallback{


    FloatingActionButton plusbutton;
    RecyclerView recyclerView;
    public static FoodOverview foodOverview;
    Button proceed;
    CalendarView calendar;
    DBArguments dbArguments;
    String currentDate;
    ArrayList<FoodObject> foods;
    DBArguments data;



    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_food);
        data = new DBArguments(this);
        final Calendar dateCalendar = Calendar.getInstance();
        final SimpleDateFormat formatdate = new SimpleDateFormat("dd/MM/yyyy");
        final Long[] hej = new Long[1];
         currentDate = formatdate.format(dateCalendar.getTime());

        setview(currentDate);

        plusbutton = (FloatingActionButton) findViewById(R.id.plusbutton);
        plusbutton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent jud = new Intent(getApplicationContext(), PlusButtonActivity.class);
                jud.putExtra("dato", formatdate.format(dateCalendar.getTime()));
                startActivity(jud);
            }
        });

        proceed = (Button) findViewById(R.id.button);

        proceed.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent datavisualize = new Intent(getApplicationContext(), ViewDataActivity.class);
                startActivity(datavisualize);
            }
        });

        calendar = (CalendarView) findViewById(R.id.calendar);

        calendar.setOnDateChangeListener(new CalendarView.OnDateChangeListener() {
            @Override
            public void onSelectedDayChange(@NonNull CalendarView calendarView, int year, int month, int day) {
                hej[0] = calendar.getDate();
                dateCalendar.setTimeInMillis(hej[0]);
                System.out.println("Todays date is:  " + formatdate.format(dateCalendar.getTime()));
                currentDate = formatdate.format(dateCalendar.getTime());
                setview(currentDate);
            }
        });


    }

    @Override
    public void onItemClick(View view, int position) {

    }

    void setview(String currentDate){
        foodOverview = new FoodOverview(data.getallfoods(currentDate), this);

        foodOverview.setitemClickCallback(this);
        recyclerView = (RecyclerView) findViewById(R.id.recycleview);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        recyclerView.setAdapter(foodOverview);
        foodOverview.notifyDataSetChanged();

    }
}