package com.example.adama.response;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;

import java.util.ArrayList;

//push

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

    public void DeleteDatabase(){
        dbHandler.onUpgrade(sqLiteDatabase,1,2);
    }

    public void CreateDatabase(){ dbHandler.onCreate(sqLiteDatabase);}

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
        return cursor;
    }

    public ArrayList<FoodTest> getallfoods(){
        ArrayList<FoodTest> arrayList2 = new ArrayList<>();
        Cursor foodpicker = selectFood_Test();
        int i = 0;
        foodpicker.moveToFirst();
        while (!foodpicker.isAfterLast()){
            arrayList2.add(i, new FoodTest(foodpicker.getString(1), foodpicker.getInt(2), foodpicker.getInt(3)));
            System.out.println("Det virker");
            i++;
            foodpicker.moveToNext();
        }
        return arrayList2;
    }

    public Cursor selectEat(){
        String[] columns = new String[] {DBHandler.EAT_ID, DBHandler.EAT_USER, DBHandler.EAT_FOOD};

        Cursor cursor = sqLiteDatabase.query(true,DBHandler.TABLE_EAT,columns,null,null,null,null,null,null);
        if(cursor !=null){
            cursor.moveToFirst();
        }
        System.out.println(cursor);
        System.out.println("SUT MN KIN KAT LORTET VIRKER IKKE");
        return cursor;
    }

}
