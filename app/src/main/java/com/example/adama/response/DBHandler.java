package com.example.adama.response;

import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import java.lang.ref.Reference;

/**
 * Created by Adama on 4/4/2017.
 */

public class DBHandler extends SQLiteOpenHelper {


    // Database Version
    private static final int DATABASE_VERSION = 1;
    // Database Name
    private static final String DATABASE_NAME = "caloriesInfo";
    // Contacts table name
    public static final String TABLE_CALORIES = "calioriesTable";
    public static final String TABLE_FOOD = "foodTable";

    // User Table Columns information
    public static final String USER_ID ="id";
    public static final String USER_NAME = "name";
    public static final String USER_AGE = "age";
    public static final String USER_WEIGTH ="weigth";
    public static final String USER_GENDER ="gender";
    public static final String USER_FOOD = "user_food";

    //Food Table information
    public static final String FOOD_ID ="id";
    public static final String FOOD_NAME ="name";
    public static final String FOOD_CALORIE = "calorie";
    public static final String FOOD_QUANTITY = "quantity";





    public DBHandler(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }


    @Override
    public void onCreate(SQLiteDatabase db) {

        String CREATE_FOOD_TABLE = "CREATE TABLE " + TABLE_FOOD + "("
                + FOOD_ID + " INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                + FOOD_NAME + " TEXT,"
                + FOOD_CALORIE + " INTEGER,"
                + FOOD_QUANTITY + " INTEGER " + ")";


        String CREATE_CALORIES_TABLE = "CREATE TABLE " + TABLE_CALORIES + "("
                + USER_ID + " INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                + USER_NAME + " TEXT,"
                + USER_AGE + " INTEGER,"
                + USER_WEIGTH + " INTEGER,"
                + USER_GENDER + " TEXT " + ")";
               // + USER_FOOD + " INTEGER,"
              //  + "FOREIGN KEY(" + USER_FOOD + ")" + "REFERENCE" + TABLE_FOOD + "(" + FOOD_ID + ")"  + ")";


        db.execSQL(CREATE_CALORIES_TABLE);
        db.execSQL(CREATE_FOOD_TABLE);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {

        //Drop old table if it exist
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_CALORIES);
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_FOOD);
        onCreate(db);



    }
}
