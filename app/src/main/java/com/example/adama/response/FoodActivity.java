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
        Calendar dateCalendar = Calendar.getInstance();
        SimpleDateFormat formatdate = new SimpleDateFormat("dd/MM/yyyy");
        currentDate = formatdate.format(dateCalendar.getTime());

        setview(currentDate);

        plusbutton = (FloatingActionButton) findViewById(R.id.plusbutton);
        plusbutton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent jud = new Intent(getApplicationContext(), PlusButtonActivity.class);
                jud.putExtra("dato", currentDate);
                startActivity(jud);
            }
        });

        proceed = (Button) findViewById(R.id.button);

        proceed.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent datavisualize = new Intent(getApplicationContext(), ViewDataActivity.class);
                datavisualize.putExtra("date", currentDate);
                startActivity(datavisualize);
            }
        });

        calendar = (CalendarView) findViewById(R.id.calendar);

        calendar.setOnDateChangeListener(new CalendarView.OnDateChangeListener() {
            @Override
            public void onSelectedDayChange(@NonNull CalendarView calendarView, int year, int month, int day) {
                month = month +1;
                String dd = "";
                String MM = "";
                if(day <9)dd = "0"+day;
                if(month<9)MM = "0"+month;
                currentDate = ""+dd+"/"+MM+"/"+year;
                System.out.println(currentDate);
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