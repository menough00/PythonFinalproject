$("#collapse-all").click(
    function(){

        $(".accordion button").addClass("collapsed");
        $(".accordion section").removeClass("show");
    }
);
$("#show-all").click(
    function(){

        $(".accordion button").removeClass("collapsed");
        $(".accordion section").addClass("show");
    }
);

