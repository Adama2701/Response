package com.example.adama.response;

import android.content.Intent;
import android.database.Cursor;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.AdapterView;
import android.widget.Button;
//push

public class MainActivity extends AppCompatActivity implements AdapterView.OnItemSelectedListener
{
Button mainbutton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        //TESTING DATABASE
        DBArguments data = new DBArguments(this);

        DBHandler kattne = new DBHandler(this);

        data.DeleteDatabase();


        //data.InsertFoodTest(new FoodTest( "Banana", 500,1));
        //data.InsertTest(new UserObject("Kenneth", 26, 65, "Man"));
        //data.InsertEatTest(new EatTest(1,1));




        //FoodTest dummydata = new FoodTest(1, "Adama", 2000, 3 );
        //data.InsertFoodTest(dummydata);

        Cursor cursor = data.selectEat();

        cursor.moveToFirst();
        while (!cursor.isAfterLast()) {
            System.out.println(cursor.getColumnName(0)+": "+cursor.getInt(0)+ " | "+ cursor.getColumnName(1)+ ": "+ cursor.getInt(1)+" | "+cursor.getColumnName(2)+
                    ": "+cursor.getInt(2) + " | ");
            cursor.moveToNext();
        }
        //TESTING DATABASE ENDS HERE

        mainbutton = (Button) findViewById(R.id.mainbutton);


        mainbutton.setOnClickListener(new View.OnClickListener(){

            @Override
            public void onClick(View view) {
                Intent ja = new Intent(getApplicationContext(), FoodActivity.class);
                startActivity(ja);
            }
        });
}


    @Override
    public void onItemSelected(AdapterView<?> adapterView, View view, int i, long l) {

    }

    @Override
    public void onNothingSelected(AdapterView<?> adapterView) {

    }
}
