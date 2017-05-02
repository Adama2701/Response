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
                "1 Beer: 150 cal", "1 Light Beer: 95 cal", "1 Cup Blackberries: 75 cal", "1 Cup Blueberries: 80 cal",
        "1 Spear Broccoli: 40 cal", "1 Carrot: 45 cal", "1 portion of Cherrios: 110 cal", "1 Chicken Breast Roast: 140 cal",
        "1 Chicken Drumstick: 75 cal", "1 portion of Cornflakes: 110 cal", "1 Croissaint: 235 cal", "1 Danish Pastry: 235 cal",
        "1 Fried Egg: 90 cal", "1 Hard Cooked Egg: 75 cal", "1 Poached Egg: 75 cal", "1 Scrambled Egg: 100 cal",
        "1 Frankfurter sausage: 145 cal", "1 Hamburger: 445 cal", "1 Cup Vanilla Ice Cream (11% fat): 270 cal", "1 Kiwi: 45 cal",
                "1 Lemon: 15 cal", "1 cup Macaroni: 190 cal", "1 Mango: 135 cal", "1 TBSP Mayonnaise: 100 cal",
                "1 Cup Milk: 150 cal", "1 Cup Egg-Noodles: 200 cal", "1 Chopped Onion: 55 cal",
                "1 Cup Orange juice: 150 cal", "1 Orange: 60 cal", "1 Pancake: 60 cal", "1 Cup Peanuts (salted): 840 cal",
                "1 Cup Peanuts (unsalted): 840 cal", "1 Cup Pineapple: 75 cal", "1 Pita Bread: 165 cal",
                "1 Slice Pizza Cheese: 290 cal", "1 Cup Popcorn (salted): 55 cal", "1 Pork Chop Loin: 275 cal",
                "1 Row of Pork Ribs: 300 cal", "10 Potato Chips: 105 cal", "1 Portion Potato Salad: 370 cal",
                "1 Potato baked without skin: 145 cal", "1 Potato baked with skin: 220 cal", "1 Boiled Potato: 120 cal",
                "1 Cup mashed Potatoes: 240 cal", "1 cup Pudding (Cholocate): 220 cal", "1 cup Pudding (Vanilla): 145 cal",
                "1 Cup Raspberries: 60 cal", "1 Cup Rice cooked: 230 cal", "1 Salami slice: 72.5 cal", "1 Salmon baked: 140 cal",
                "1 Salmon smoked: 150 cal", "1 TBSP Sour Cream: 25 cal", "1 Cup Spaghetti: 290 cal", "1 Cup Spinach: 25 cal",
                "1 cup Strawberries: 45 cal", "1 cup Sunflower oil: 1925 cal", "1 Cup Tomato Paste: 220 cal", "1 Tomato Soup (canned): 220 cal",
                "1 Tomato: 25 cal", "1 Cup Tuna Salad: 375 cal", "1 slice of Turkey Ham: 37.5 cal", "1 Piece of Turkey Roasted: 50 cal",
                "1 Waffle: 245 cal", "1 Watermelon piece: 155 cal", "1 slice Wheat Bread: 65 cal", "1 Loaf White Bread: 1210 cal",
                "1 Cup Whipped Cream: 820 cal", "1 portion Yogurt: 140 cal"
        };

        ArrayList<String> foodlist = new ArrayList<String>();

        foodlist.addAll(Arrays.asList(food) );

        listadapter = new ArrayAdapter<String>(this, R.layout.foodview, R.id.foods, foodlist);

        listView.setAdapter(listadapter);
    }
}
