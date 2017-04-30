package com.example.adama.response;

import android.content.Intent;
import android.database.Cursor;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;


//push
public class    PlusButtonActivity extends AppCompatActivity {
Button complete;
    EditText enterfood;
    EditText enteramount;
    EditText entercalorie;
    boolean foodentered = false;



    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_plus_button);

        final DBArguments data = new DBArguments(this);

        Cursor cursor = data.selectFood_Test();

        enterfood = (EditText) findViewById(R.id.enterfood);
        enteramount = (EditText) findViewById(R.id.enteramount);
        entercalorie = (EditText) findViewById(R.id.entercalorie) ;

        cursor.moveToFirst();


        complete = (Button) findViewById(R.id.complete);
        complete.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent xa = new Intent(getApplicationContext(), FoodActivity.class);
                    int calorie = Integer.parseInt(entercalorie.getText().toString());
                    int amountfood = Integer.parseInt(enteramount.getText().toString());
                    data.InsertFoodTest(new FoodObject(enterfood.getText().toString(), calorie , amountfood, "")); //PRØVER AT INDSÆTTE TIME

                startActivity(xa);

                entercalorie.setText(" ");
                enterfood.setText(" ");
                enteramount.setText(" ");

            }



        });
    }}

