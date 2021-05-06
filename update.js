var product="";
var cat_id="";
var is_custom=false;

function ajax_search(){
    let new_product=$("#product").val();

    let new_cat_id=$("#category").val();

    if(new_product!=""&&( is_custom!=$("#custom").is(":checked")||product !=new_product || cat_id!=new_cat_id)){
        is_custom=$("#custom").is(":checked");
        product=new_product;
        cat_id = new_cat_id;
        let results_table=$("#product-form")
        let category=$("#category").val();
        let custom=$("#custom").is(":checked");
        if(custom){
            query={method: "POST", url: "/search",
                data:{product: product, category: category, custom: 1}};

        }
        else{
            query={method: "POST", url: "/search",
                data:{product: product, category: category}};
        }
        console.log("query: "+query)
        $.ajax(query).done(function(results){
            results_table.empty();
            let header = $(`<li class='list-group-item'>
                                <div class="row no-gutter">
                                    <div class="col-5 col-md-3">Name</div>
                                    <div class="col-4 col-md-2">Category</div>
                                    <div class="col-3 col-md-2">Quantity</div>
                                    <div class="col-5 col-md-2">Expiration Date</div>
                                    <div class="col-5 col-md-2">Cost per item</div>
                                    <div class="col-2 col-md-1">Add item</div>
                                </div>
                           </li>`);
            results_table.append(header);
            if (!results || results.length == 0) {
                let row = $(`<li class="list-group-item">
                                <div class="row no-gutter">
                                    <div class="col-12">No Results</div>
                                </div>
                            </li>`);
                results_table.append(row);
            }
            else
            {

            $.each(results,function(index){
                /*
                let form=$("<form id='add"+results[index]["id"]+"'></form>");
                let row=$("<tr></tr>");
                row.append($("<td><p>"+results[index]["name"]+"</p></td>"));
                row.append($("<td><p>"+results[index]["category"]+"</p></td>"));
                row.append($("<td><input class='form-control'  type='number' min='0' max='100'/></td>"));
                row.append($("<td><input class='form-control' name='exp' placeholder="exp date" type='date'/></td>"));
                row.append($("<td><input class='form-control' name='cost' placeholder="cost" type='number' min='0' max='10000' step='.01'/></td>"));
                row.append($("<td><input class='form-control' value='add' type='submit'/></td>"));
                row.css({height:"20px"});
                form.append(row);
                results_table.append(form);
                */
                //console.log(results[index]["id"]);
                let user_id = 0;
                if ("user_id" in results[index]) {
                    user_id = results[index]["user_id"]
                }
                let form = $(`<li class='list-group-item'>
                              <form id='add${results[index]["id"]}' action='/update' method='post'>
                              <div class="row no-gutter">
                                    <div class="col-5 col-md-3">${results[index]["name"]}</div>
                                    <div class="col-4 col-md-2">${results[index]["category"]}</div>
                                    <div class="d-none"><input class='form-control form-control-sm' name='id' type='number' value='${results[index]["id"]}' required/></div>
                                    <div class="d-none"><input class='form-control form-control-sm' name='user-id' type='number' value='${user_id}' /></div>
                                    <div class="col-3 col-md-2"><input class='form-control form-control-sm' name='qty' placeholder="qty" type='number' min='0' max='100' required/></div>
                                    <div class="col-5 col-md-2"><input class='form-control form-control-sm' name='exp' placeholder="exp date" type='date' required/></div>
                                    <div class="col-5 col-md-2"><input class='form-control form-control-sm' name='cost' placeholder="cost" type='number' min='0' max='10000' step='.01' required/></div>
                                    <div class="col-2 col-md-1"><input class='form-control form-control-sm' value='+' type='submit'/></div>
                              </div>
                              </form>
                              </li>`);
                results_table.append(form);

            });
            }
        });
    }
}
setInterval(ajax_search,1000);
