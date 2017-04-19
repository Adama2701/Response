package com.example.adama.response;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.Spinner;
//push

public class MainActivity extends AppCompatActivity implements AdapterView.OnItemSelectedListener
{
Button mainbutton;
Spinner spinner;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        //TESTING DATABASE
        DBArguments data = new DBArguments(this);



        data.InsertFoodTest(new FoodTest( "katten", 2,2));

        DBHandler kat = new DBHandler(this);

        //FoodTest dummydata = new FoodTest(1, "Adama", 2000, 3 );
        //data.InsertFoodTest(dummydata);

        //Cursor cursor = data.selectFood_Test();

        //cursor.moveToFirst();
        //while (!cursor.isAfterLast()) {
           // System.out.println(cursor.getColumnName(0)+": "+cursor.getInt(0)+ " | "+ cursor.getColumnName(1)+ ": "+ cursor.getString(1)+" | "+cursor.getColumnName(2)+
         //           ": "+cursor.getInt(2) + " | "+ cursor.getColumnName(3)+ ": "+ cursor.getString(3)+" | ");
       //     cursor.moveToNext();
       // }
        //TESTING DATABASE ENDS HERE

        mainbutton = (Button) findViewById(R.id.mainbutton);

        spinner = (Spinner) findViewById(R.id.spinner);

        ArrayAdapter adapter = ArrayAdapter.createFromResource(this, R.array.age, android.R.layout.simple_spinner_item);
        spinner.setAdapter(adapter);
        spinner.setOnItemSelectedListener(this);

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
