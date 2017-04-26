package com.example.adama.response;

/**
 * Created by adama on 25-04-2017.
 */

public class EatObject {


    // Food information
    private int eat_id;
    private Integer eat_user_id;
    private Integer eat_food_id;


    public EatObject(Integer eat_user_id, Integer eat_food_id) {
        this.eat_user_id = eat_user_id;
        this.eat_food_id = eat_food_id;

    }

    public Integer getEat_user_id() {
        return eat_user_id;
    }

    public Integer getEat_food_id() {
        return eat_food_id;
    }

    }


