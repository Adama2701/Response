package com.example.adama.response;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.Button;

public class ThemeActivity extends AppCompatActivity {

    Button gain;
    Button lose;
    Button healthy;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_theme);

        gain = (Button) findViewById(R.id.gain);
        lose = (Button) findViewById(R.id.lose);
        healthy = (Button) findViewById(R.id.healthy);

        gain.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent da = new Intent(getApplicationContext(), WelcomeActivity.class);
                startActivity(da);
            }
        });
        lose.setOnClickListener((new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent er  = new Intent(getApplicationContext(), WelcomeActivity.class);
                startActivity(er);
            }
        }));
        healthy.setOnClickListener((new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent qw = new Intent(getApplicationContext(), WelcomeActivity.class);
                startActivity(qw);
            }
        }));
    }
}
