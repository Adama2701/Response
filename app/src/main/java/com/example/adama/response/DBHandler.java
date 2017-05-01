package com.example.adama.response;

import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;

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
    public static final String TABLE_EAT = "eatTable";

    // User Table Columns information
    public static final String USER_ID = "id";
    public static final String USER_NAME = "name";
    public static final String USER_AGE = "age";
    public static final String USER_GENDER = "gender";

    //Food Table information
    public static final String FOOD_ID = "id";
    public static final String FOOD_NAME = "name";
    public static final String FOOD_CALORIE = "calorie";
    public static final String FOOD_QUANTITY = "quantity";
    public static final String FOOD_DATE = "date";


    // Eat Table information
    public static final String EAT_ID = "id";
    public static final String EAT_FOOD = "food_id";
    public static final String EAT_USER = "user_id";


    public DBHandler(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {


        String CREATE_FOOD_TABLE = "CREATE TABLE " + TABLE_FOOD + "("
                + FOOD_ID + " INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                + FOOD_NAME + " TEXT,"
                + FOOD_CALORIE + " INTEGER, "
                + FOOD_QUANTITY + " INTEGER, "
                + FOOD_DATE + " TEXT " + ")";


        String CREATE_USER_TABLE = "CREATE TABLE " + TABLE_USER + "("
                + USER_ID + " INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                + USER_NAME + " TEXT,"
                + USER_AGE + " INTEGER,"
                + USER_GENDER + " TEXT " + ")";

        String CREATE_EAT_TABLE = "CREATE TABLE " + TABLE_EAT + "("
                + EAT_ID + " INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                + EAT_USER + " INTEGER, "
                + EAT_FOOD + " INTEGER, "
                + " FOREIGN KEY (" + EAT_USER + ") REFERENCES  " + TABLE_USER + "(" + USER_ID + "),"
                + " FOREIGN KEY (" + EAT_FOOD + ") REFERENCES  " + TABLE_FOOD + "(" + FOOD_ID + "));";


        db.execSQL(CREATE_USER_TABLE);
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

    public void dropRows(SQLiteDatabase db) {

        db.execSQL(" DELETE FROM " + TABLE_FOOD);
    }


    public int  foo(SQLiteDatabase db){
        Cursor cursor = db.rawQuery("SELECT calorie  FROM  foodTable ",null);
        Cursor food_cursor = db.rawQuery("SELECT * FROM foodTable",null);

        Cursor user_age_cusor = db.rawQuery("SELECT age FROM userTable",null);
        Cursor user_gender_cursor = db.rawQuery("SELECT gender FROM userTable",null);

        final SimpleDateFormat formatdate = new SimpleDateFormat("dd/MM/yyyy");
        String date = "";
        Calendar calendar = Calendar.getInstance();
        String today = formatdate.format(calendar.getTime());



        List<Integer> a = new ArrayList<Integer>();
        int sum = 0;
        if (food_cursor.moveToFirst()){
            do{
                if(food_cursor.getString(food_cursor.getColumnIndex(FOOD_DATE)).contains(today)) {

                    String data = food_cursor.getString(food_cursor.getColumnIndex(FOOD_CALORIE));
                    int kat = Integer.parseInt(data);
                    a.add(kat);
                    System.out.println(data);
                }

                }while(food_cursor.moveToNext());
                for ( int x:a){
                    sum = sum + x;
                }
            }
        food_cursor.close();



        System.out.println("KATTEN KENNETHS DATO ER : " + date);
        food_cursor.close();

        List<Integer> user_age_list = new ArrayList<Integer>();
        int age = 0;

        if (user_age_cusor.moveToFirst()){
            do{

                String user_data = user_age_cusor.getString(user_age_cusor.getColumnIndex(USER_AGE));
                int user_age = Integer.parseInt(user_data);
                user_age_list.add(user_age);

            }while(cursor.moveToNext());
            for (int user_age: user_age_list){

                age = user_age;
            }

        }
        user_age_cusor.close();

        String gender = "";

        if (user_gender_cursor.moveToFirst()){
            do{

                String user_gender_data = user_gender_cursor.getString(user_gender_cursor.getColumnIndex(USER_GENDER));

                gender = user_gender_data;
            }while(user_gender_cursor.moveToNext());


        }
        user_gender_cursor.close();

       System.out.println("SUMMEN ER :" + sum);
       if (age > 8 && sum > 1000 && gender.matches("Male"))
       {System.out.println( "You have eaten too many calories, you need to cut down " + (sum - 1500));}

        return sum;

    }

}

