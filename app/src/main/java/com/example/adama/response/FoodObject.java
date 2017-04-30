package com.example.adama.response;

/**
 * Created by adama on 05-04-2017.
 */
//push


public class FoodObject {

    // Food information
    private int food_id;
    private String food_name;
    private int calorie;
    private int quantity;
    private String time;

    public FoodObject(String food_name, int calorie, int quantity, String time) {
        this.food_name = food_name;
        this.calorie = calorie;
        this.quantity = quantity;
        this.time = time;
    }

    public int getFood_id() {
        return food_id;
    }

    public String getFood_name() {
        return food_name;
    }

    public int getCalorie() {return calorie;}


    public int getQuantity() {
        return quantity;
    }

    public String getTime() {return time;}



}
