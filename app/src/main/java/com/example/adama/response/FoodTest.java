package com.example.adama.response;

/**
 * Created by adama on 05-04-2017.
 */
//push


public class FoodTest {

    // Food information
    private int food_id;
    private String food_name;
    private int quantity;

    public FoodTest(String food_name, int quantity) {
        this.food_name = food_name;
        this.quantity = quantity;
    }

    public int getFood_id() {
        return food_id;
    }

    public String getFood_name() {
        return food_name;
    }


    public int getQuantity() {
        return quantity;
    }




}
