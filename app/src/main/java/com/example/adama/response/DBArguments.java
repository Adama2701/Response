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
        content.put(DBHandler.USER_NAME,test.getName());
        content.put(DBHandler.USER_AGE,test.getAge());
        content.put(DBHandler.USER_WEIGTH,test.getWeigth());
        content.put(DBHandler.USER_GENDER,test.getGender());

        return sqLiteDatabase.insert(DBHandler.TABLE_CALORIES,null,content);
    }

    public Cursor selectTest(){
        String[] columns = new String[] {DBHandler.USER_ID, DBHandler.USER_NAME, DBHandler.USER_AGE, DBHandler.USER_WEIGTH, DBHandler.USER_GENDER};

        Cursor cursor = sqLiteDatabase.query(true,DBHandler.TABLE_CALORIES,columns,null,null,null,null,null,null);
        if(cursor !=null){
            cursor.moveToFirst();
        }
        System.out.println(cursor);
        return cursor;
    }

    public long InsertFoodTest(FoodTest foodtest){
        ContentValues content = new ContentValues();
        content.put(DBHandler.FOOD_NAME,foodtest.getFood_name());
        content.put(DBHandler.FOOD_CALORIE,foodtest.getCalorie());
        content.put(DBHandler.FOOD_QUANTITY,foodtest.getQuantity());

        return sqLiteDatabase.insert(DBHandler.TABLE_FOOD,null,content);
    }

    public Cursor selectFood_Test(){
        String[] columns = new String[] {DBHandler.FOOD_ID, DBHandler.FOOD_NAME, DBHandler.FOOD_CALORIE, DBHandler.FOOD_QUANTITY};

        Cursor cursor = sqLiteDatabase.query(true,DBHandler.TABLE_FOOD,columns,null,null,null,null,null,null);
        if(cursor !=null){
            cursor.moveToFirst();
        }
        System.out.println(cursor);
        return cursor;
    }

}
