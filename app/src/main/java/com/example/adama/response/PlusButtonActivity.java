package com.example.adama.response;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.Button;
//push
public class PlusButtonActivity extends AppCompatActivity {
Button complete;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_plus_button);

        complete = (Button) findViewById(R.id.complete);
        complete.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent xa = new Intent(getApplicationContext(), FoodActivity.class);
                startActivity(xa);
            }
        });

        final Button amount = (Button) findViewById(R.id.amount);
        amount.setTag(1);
        amount.setText("1");
        amount.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                final int status = (Integer) v.getTag();
                if (status == 1) {
                    amount.setText("2");
                    v.setTag(0);
                } else {
                    amount.setText("1");
                    v.setTag(1);

                }
            }

        });
    }}

