package com.example.adama.response;

import android.content.Intent;
import android.database.Cursor;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;


public class MainActivity extends AppCompatActivity
{
    Button mainbutton;
    EditText editName;
    EditText sexEdit;
    EditText age;
    boolean hasUser = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        final DBArguments data = new DBArguments(this);

        Cursor cursor = data.selectUser();

        mainbutton = (Button) findViewById(R.id.mainbutton);
        editName = (EditText) findViewById(R.id.editName);
        sexEdit = (EditText) findViewById(R.id.sexedit);
        age = (EditText) findViewById(R.id.age);


        cursor.moveToFirst();
        if (cursor.getCount()>0){
            hasUser = true;
            editName.setText(cursor.getString(1));
            age.setText(cursor.getInt(2)+"");
            sexEdit.setText(cursor.getString(3));

        }

        mainbutton.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View view) {
                Intent ja = new Intent(getApplicationContext(), FoodActivity.class);
                if (!hasUser){
                    int numberage = Integer.parseInt(age.getText().toString());
                    data.InsertUser(new UserObject(editName.getText().toString(), numberage, sexEdit.getText().toString()));

                }
                startActivity(ja);
            }


        });


    }


}
