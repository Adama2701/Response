package com.example.adama.response;

/**
 * Created by filipgusak on 18/04/2017.
 */
//push

public class FoodObject {
    private String Id;
    private String Name;
    private int Calorie;
    private int Quantity;

    public FoodObject(String Id, String Name, int Calorie, int Quantity){
        this.Id = Id;
        this.Name = Name;
        this.Calorie = Calorie;
        this.Quantity = Quantity;
    }

    public String getId() {
        return Id;
    }

    public void setId(String id) {
        Id = id;
    }

    public String getName() {
        return Name;
    }

    public void setName(String name) {
        Name = name;
    }

    public int getCalorie() {
        return Calorie;
    }

    public void setCalorie(int calorie) {
        Calorie = calorie;
    }

    public int getQuantity() {
        return Quantity;
    }

    public void setQuantity(int quantity) {
        Quantity = quantity;
    }
}
