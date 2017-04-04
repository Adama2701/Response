package com.example.adama.response;

/**
 * Created by Adama on 4/4/2017.
 */

public class Test {

    private int id;
    private String name;
    private int age;
    private int weigth;
    private String gender;


    Test( String name, int age, int weigth, String gender){

        this.name = name;
        this.age = age;
        this.weigth = weigth;
        this.gender = gender;

    }

    public int getId(){
        return id;
    }



    public String getName(){
        return name;
    }

    public int getAge() {
        return age;
    }

    public int getWeigth() {
        return weigth;
    }

    public String getGender() {
        return gender;
    }

}