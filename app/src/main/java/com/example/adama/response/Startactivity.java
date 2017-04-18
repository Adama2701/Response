package com.example.adama.response;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
//push
public class Startactivity extends AppCompatActivity {
    Button proceed;
    DBArguments dbArguments;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_startactivity);

        dbArguments = new DBArguments(this);
        dbArguments.InsertFoodTest(new FoodTest(1, "hej", 2, 2));

        proceed = (Button) findViewById(R.id.proceed);


        proceed.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent fp = new Intent(getApplicationContext(), MainActivity.class);
                startActivity(fp);
            }
        });
    }


}
