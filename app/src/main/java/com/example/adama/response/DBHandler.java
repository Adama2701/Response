package com.example.adama.response;

import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

/**
 * Created by Adama on 4/4/2017.
 */

public class DBHandler extends SQLiteOpenHelper {


    // Database Version
    private static final int DATABASE_VERSION = 1;
    // Database Name
    private static final String DATABASE_NAME = "caloriesInfo";
    // Contacts table name
    public static final String TABLE_USER = "userTable";
    public static final String TABLE_FOOD = "foodTable";
    public static final String TABLE_LIST_FOOD = "listfoodTable";
    public static final String TABLE_EAT = "eatTable";

    // User Table Columns information
    public static final String USER_ID ="id";
    public static final String USER_NAME = "name";
    public static final String USER_AGE = "age";
    public static final String USER_GENDER ="gender";

    //Food Table information
    public static final String FOOD_ID ="id";
    public static final String FOOD_NAME ="name";
    public static final String FOOD_QUANTITY = "quantity";

    // Food List table information
    public static final String LIST_FOOD_ID = "id";
    public static final String LIST_FOOD_NAME =  "name";
    public static final String LIST_FOOD_CALORIE = "calorie";

    // Eat Table information
    public static final String EAT_ID = "id";
    public static final String EAT_FOOD = "food_id";
    public static final String EAT_USER = "user_id";


    public DBHandler(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {

        String CREATE_LIST_FOOD_TABLE = "CREATE TABLE " + TABLE_LIST_FOOD + "("
                + LIST_FOOD_ID + " INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                + LIST_FOOD_NAME + " TEXT,"
                + LIST_FOOD_CALORIE + " INTEGER, " + ")";


        String CREATE_FOOD_TABLE = "CREATE TABLE " + TABLE_FOOD + "("
                + FOOD_ID + " INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                + FOOD_NAME + " TEXT,"
                + FOOD_QUANTITY + " INTEGER " + ")";


        String CREATE_CALORIES_TABLE = "CREATE TABLE " + TABLE_USER + "("
                + USER_ID + " INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                + USER_NAME + " TEXT,"
                + USER_AGE + " INTEGER,"
                + USER_GENDER + " TEXT " + ")";

        String CREATE_EAT_TABLE = "CREATE TABLE " + TABLE_EAT + "("
                + EAT_ID + " INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                + EAT_USER + " INTEGER, "
                + EAT_FOOD + " INTEGER, "
                + " FOREIGN KEY ("+EAT_USER+") REFERENCES  "+ TABLE_USER +"(" + USER_ID + "),"
                + " FOREIGN KEY ("+EAT_FOOD+") REFERENCES  "+TABLE_FOOD+"(" + FOOD_ID + "));";

        db.execSQL(CREATE_LIST_FOOD_TABLE);
        db.execSQL(CREATE_CALORIES_TABLE);
        db.execSQL(CREATE_FOOD_TABLE);
        db.execSQL(CREATE_EAT_TABLE);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {

        //Drop old table if it exist
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_USER);
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_FOOD);
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_EAT);
        onCreate(db);

    }

    public void dropRows(SQLiteDatabase db){

        db.execSQL(" DELETE * FROM "+ TABLE_EAT);
    }
}
