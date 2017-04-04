package com.example.adama.response;

import android.content.Context;
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
    public static final String TABLE_CALORIES = "calioriesTable";

    // Guess Table Columns names
    public static final String KEY_ID ="id";
    public static final String KEY_NAME = "name";
    public static final String KEY_AGE = "age";
    public static final String KEY_WEIGTH ="weigth";
    public static final String KEY_GENDER ="gender";



    public DBHandler(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }


    @Override
    public void onCreate(SQLiteDatabase db) {
        String CREATE_cALORIES_TABLE = "CREATE TABLE " + TABLE_CALORIES + "("
                + KEY_ID + " INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                + KEY_NAME + " TEXT,"
                + KEY_AGE + " INTEGER,"
                + KEY_WEIGTH + " INTEGER,"
                + KEY_GENDER + " TEXT " + ")";

        db.execSQL(CREATE_cALORIES_TABLE);


    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {

        //Drop old table if it exist
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_CALORIES);
        onCreate(db);



    }
}
