package com.example.adama.response;

import android.content.Context;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.ArrayList;

/**
 * Created by filipgusak on 18/04/2017.
 */

public class FoodOverview extends RecyclerView.Adapter<FoodOverview.adapterclass> {

    private itemClickCallback callback;
    private ArrayList<FoodTest> arrayList;
    private LayoutInflater layoutInflater;

    public FoodOverview(ArrayList<FoodTest> foodObjectArrayList, Context context){
        this.layoutInflater= LayoutInflater.from(context);
        this.arrayList= foodObjectArrayList;
    }

    @Override
    public adapterclass onCreateViewHolder(ViewGroup parent, int viewType) {
        View view = layoutInflater.inflate(R.layout.entries, parent, false);
        return new adapterclass(view);
    }

    @Override
    public void onBindViewHolder(adapterclass holder, int position) {
        FoodTest foodObject = arrayList.get(position);
        holder.leftview.setText(foodObject.getFood_name());
        holder.rightview.setText(String.valueOf(foodObject.getQuantity()));

    }

    @Override
    public int getItemCount() {
        return arrayList.size();
    }

    public interface itemClickCallback{
    void onItemClick(View view, int position);
}
public void setitemClickCallback(final itemClickCallback itemClickCallback){
    this.callback = itemClickCallback;
}

class adapterclass extends RecyclerView.ViewHolder implements View.OnClickListener {
    private TextView leftview;
    private TextView rightview;
    private View container;



    public adapterclass(View entityview){
        super (entityview);

        leftview = (TextView) entityview.findViewById(R.id.leftview);
        rightview = (TextView) entityview.findViewById(R.id.rightview);
        container = entityview.findViewById(R.id.cardview);
        container.setOnClickListener(this);
    }

    @Override
    public void onClick(View view) {
        if (view.getId() == R.id.cardview) {
            callback.onItemClick(view, getAdapterPosition());

        }
    }
}}
