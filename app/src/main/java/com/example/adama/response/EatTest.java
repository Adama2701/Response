package com.example.adama.response;

/**
 * Created by adama on 25-04-2017.
 */

public class EatTest {


    // Food information
    private int eat_id;
    private String user_name;
    private String food_name;


    public EatTest(String user_name, String food_name) {
        this.user_name = user_name;
        this.food_name = food_name;

    }

    public String getUser_name() {
        return user_name;
    }

    public String getFood_name() {
        return food_name;
    }

    }


