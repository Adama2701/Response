package com.example.adama.response;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;

/**
 * Created by Adama on 4/4/2017.
 */

public class DBArguments {
    private DBHandler dbHandler;
    private SQLiteDatabase sqLiteDatabase;

    public DBArguments(Context context){
        dbHandler = new DBHandler(context);
        sqLiteDatabase = dbHandler.getWritableDatabase();
    }

    public long InsertTest(Test test){
        ContentValues content = new ContentValues();
        content.put(DBHandler.KEY_NAME,test.getName());
        content.put(DBHandler.KEY_AGE,test.getAge());
        content.put(DBHandler.KEY_WEIGTH,test.getWeigth());
        content.put(DBHandler.KEY_GENDER,test.getGender());

        return sqLiteDatabase.insert(DBHandler.TABLE_CALORIES,null,content);
    }

    public Cursor selectTest(){
        String[] columns = new String[] {DBHandler.KEY_ID, DBHandler.KEY_NAME, DBHandler.KEY_AGE, DBHandler.KEY_WEIGTH, DBHandler.KEY_GENDER};

        Cursor cursor = sqLiteDatabase.query(true,DBHandler.TABLE_CALORIES,columns,null,null,null,null,null,null);
        if(cursor !=null){
            cursor.moveToFirst();
        }
        System.out.println(cursor);
        return cursor;
    }

}
