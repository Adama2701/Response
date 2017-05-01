package com.example.adama.response;

import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.Arrays;

public class ListFoodActivity extends AppCompatActivity {

    TextView food;
    ListView listView;
    private ArrayAdapter<String> listadapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_list_food);

        listView = (ListView) findViewById(android.R.id.list);

        String[] food = new String[] { "1 Apple: 52 cal", "1 Banana: 105 cal", "1 Beef steak: 240 cal ",
                "1 Beer: 150 cal", "1 light Beer: 95 cal", "1 cup Blackberries: 75 cal", "1 cup Blueberries: 80 cal",
        ""};

        ArrayList<String> foodlist = new ArrayList<String>();

        foodlist.addAll(Arrays.asList(food) );

        listadapter = new ArrayAdapter<String>(this, R.layout.foodview, R.id.foods, foodlist);

        listView.setAdapter(listadapter);
    }
}
