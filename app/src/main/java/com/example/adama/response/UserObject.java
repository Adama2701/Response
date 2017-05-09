package com.example.adama.response;

public class UserObject {
    // User information
    private int id;
    private String name;
    private int age;
    private String gender;

    UserObject(String name, int age, String gender){

        this.name = name;
        this.age = age;
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

    public String getGender() {
        return gender;
    }

}