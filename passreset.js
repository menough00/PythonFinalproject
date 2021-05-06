$("#username").change(
    function(){
        let username=$("#username").val().toLowerCase();
        query={method: "POST", url: "/get_questions",
                data:{username: username}};
        $.ajax(query).done(function(results){
        // if the object is not empty, we want to display the questions.
        if (!jQuery.isEmptyObject(results)&& username==results["username"]){
            $("#label-q1").html(results["sec_q1"]);
            $("#label-q2").html(results["sec_q2"]);
            console.log(results);
            }
            else
            {
                 $("#label-q1").html("waiting for username");
                 $("#label-q2").html("waiting for username");
            }
        });
    }
 );

