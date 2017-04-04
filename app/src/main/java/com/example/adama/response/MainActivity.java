package com.example.adama.response;

import android.database.Cursor;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;


public class MainActivity extends AppCompatActivity {

    Button button1;
    Button button2;
    Button button3;
    Button button4;
    ImageView imageView2;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        button1 = (Button) findViewById(R.id.button1);
        button2 = (Button) findViewById(R.id.button2);
        button3 = (Button) findViewById(R.id.button3);
        button4 = (Button) findViewById(R.id.button4);
        imageView2 = (ImageView) findViewById(R.id.imageView2);


        DBArguments  data = new DBArguments(this);
        Test foo = new Test("Adama", 26, 65, "Man");
        //data.InsertTest(foo);

        //Prints rows from database
        Cursor cursor = data.selectTest();

        cursor.moveToFirst();
        while (!cursor.isAfterLast()) {
            System.out.println(cursor.getColumnName(0)+": "+cursor.getInt(0)+ " | "+ cursor.getColumnName(1)+ ": "+ cursor.getString(1)+" | "+cursor.getColumnName(2)+
                    ": "+cursor.getInt(2)+" | "+cursor.getColumnName(3)+": "+cursor.getInt(3)+" | "+cursor.getColumnName(4)+": "+cursor.getString(4));
            cursor.moveToNext();
        }


        imageView2.setVisibility(View.INVISIBLE);

        button1.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
               System.out.println("THIS IS TARNING");
            }
        });


        button2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (!imageView2.isShown()) {
                    try {
                        Thread.sleep(500);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    imageView2.setVisibility(View.VISIBLE);

                }else{
                    imageView2.setVisibility(View.INVISIBLE);
                }
            }
        });

        button3.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (!imageView2.isShown()) {
                    try {
                        Thread.sleep(1000);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    imageView2.setVisibility(View.VISIBLE);

                }else{
                    imageView2.setVisibility(View.INVISIBLE);
                }
            }
        });

        button4.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (!imageView2.isShown()) {
                    try {
                        Thread.sleep(3000);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    imageView2.setVisibility(View.VISIBLE);

                }else{
                    imageView2.setVisibility(View.INVISIBLE);
                }
            }
        });
    }
}
