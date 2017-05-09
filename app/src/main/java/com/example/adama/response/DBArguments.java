package com.example.adama.response;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;

import java.util.ArrayList;



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

    public void deleteRowsKat() {dbHandler.dropRows(sqLiteDatabase);}

    //public void foo(){dbHandler.foo(sqLiteDatabase, );




    public long InsertUser(UserObject userObject){
        ContentValues content = new ContentValues();
        content.put(DBHandler.USER_NAME, userObject.getName());
        content.put(DBHandler.USER_AGE, userObject.getAge());
        content.put(DBHandler.USER_GENDER, userObject.getGender());

        return sqLiteDatabase.insert(DBHandler.TABLE_USER,null,content);
    }

    public Cursor selectUser(){
        String[] columns = new String[] {DBHandler.USER_ID, DBHandler.USER_NAME, DBHandler.USER_AGE, DBHandler.USER_GENDER};

        Cursor cursor = sqLiteDatabase.query(true,DBHandler.TABLE_USER,columns,null,null,null,null,null,null);
        if(cursor !=null){
            cursor.moveToFirst();
        }
        return cursor;
    }

    public long InsertFoodTest(FoodObject foodtest){
        ContentValues content = new ContentValues();
        content.put(DBHandler.FOOD_NAME,foodtest.getFood_name());
        content.put(DBHandler.FOOD_CALORIE,foodtest.getCalorie());
        content.put(DBHandler.FOOD_QUANTITY,foodtest.getQuantity());
        content.put(DBHandler.FOOD_DATE, foodtest.getTime());

        return sqLiteDatabase.insert(DBHandler.TABLE_FOOD,null,content);
    }

    public Cursor selectFood_Test(){
        String[] columns = new String[] {DBHandler.FOOD_ID, DBHandler.FOOD_NAME, DBHandler.FOOD_CALORIE, DBHandler.FOOD_QUANTITY, DBHandler.FOOD_DATE};

        Cursor cursor = sqLiteDatabase.query(true,DBHandler.TABLE_FOOD,columns,null,null,null,null,null,null);
        if(cursor !=null){
            cursor.moveToFirst();
        }
        return cursor;
    }

    public ArrayList<FoodObject> getallfoods(String date){
        ArrayList<FoodObject> arrayList2 = new ArrayList<>();
        Cursor foodpicker = selectFood_Test();
        int i = 0;
        foodpicker.moveToFirst();
        while (!foodpicker.isAfterLast()){
            if(foodpicker.getString(4).contains(date)){
                arrayList2.add(i, new FoodObject(foodpicker.getString(1),foodpicker.getInt(2), foodpicker.getInt(3), foodpicker.getString(4)));
                i++;
                foodpicker.moveToNext();
            }else {
                foodpicker.moveToNext();
            }
        }
        return arrayList2;
    }

    public Cursor selectEat(){
        String[] columns = new String[] {DBHandler.EAT_ID, DBHandler.EAT_USER, DBHandler.EAT_FOOD};

        Cursor cursor = sqLiteDatabase.query(true,DBHandler.TABLE_EAT,columns,null,null,null,null,null,null);
        if(cursor !=null){
            cursor.moveToFirst();
        }
        return cursor;
    }

    public long InsertEatTest(EatObject eattest){
        ContentValues content = new ContentValues();
        content.put(DBHandler.EAT_USER,eattest.getEat_user_id());
        content.put(DBHandler.EAT_FOOD,eattest.getEat_food_id());

        return sqLiteDatabase.insert(DBHandler.TABLE_EAT,null,content);
    }

    public int[] callFoo (String string){
        int[] temp;
        temp = dbHandler.foo(sqLiteDatabase, string);


        return temp;

    }



}
