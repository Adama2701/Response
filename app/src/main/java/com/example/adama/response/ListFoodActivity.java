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
        "1 spear Broccoli: 40 cal", "1 Carrot: 45 cal", "1 portion of Cherrios: 110 cal", "1 Chicken Breast Roast: 140 cal",
        "1 Chicken Drumstick: 75 cal", "1 portion of Cornflakes: 110 cal", "1 Croissaint: 235 cal", "1 Danish Pastry: 235 cal",
        "1 Fried Egg: 90 cal", "1 Hard Cooked Egg: 75 cal", "1 Poached Egg: 75 cal", "1 Scrambled Egg: 100 cal",
        "1 Frankfurter sausage: 145 cal", "1 Hamburger: 445 cal", "1 Cup Vanilla Ice Cream (11% fat): 270 cal",
        };

        ArrayList<String> foodlist = new ArrayList<String>();

        foodlist.addAll(Arrays.asList(food) );

        listadapter = new ArrayAdapter<String>(this, R.layout.foodview, R.id.foods, foodlist);

        listView.setAdapter(listadapter);
    }
}
