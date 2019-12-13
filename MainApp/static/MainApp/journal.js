console.log("Startings..");
$(document).ready(function(){
    function getCookie(c_name) {
        if(document.cookie.length > 0) {
            c_start = document.cookie.indexOf(c_name + "=");
            if(c_start != -1) {
                c_start = c_start + c_name.length + 1;
                c_end = document.cookie.indexOf(";", c_start);
                if(c_end == -1) c_end = document.cookie.length;
                return unescape(document.cookie.substring(c_start,c_end));
            }
        }
        return "";
    }

    $(function () {
        $.ajaxSetup({
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            }
        });
    });
});

$(document).on('submit', '#Email-form', function(e){
    e.preventDefault();

    // Start loading data

    var ISSN = document.getElementById("doiinput").value;
    var totalCitations = "(fetching)";

    if(ISSN!=="")
    {
        $.ajax({

        type:'GET',
        url:'/totalcitationsjournal/',
        timeout : 500000,
        data:{
            q:$('#doiinput').val(),
            s:$('#startyear').val(),
            e:$('#endyear').val(),
        },

        success:function(json){

            totalCitations = json['totalCitations'];

        },

        error: function(jqXHR, textStatus, errorThrown) {

            console.log(jqXHR.status + ": " + jqXHR.responseText);

        }

        });

        showloading(e);

        var duration = 8000000,
        interval = 5000,
        intervalTimer;

        intervalTimer = setInterval(function() {
            getemails(ISSN, totalCitations);
        }, interval);

        setTimeout(function() {
            clearInterval(intervalTimer);
        }, duration);

        $.ajax({

        type:'GET',
        url:'/journal/',
        data:{
            q:$('#doiinput').val(),
            s:$('#startyear').val(),
            e:$('#endyear').val(),
        },

        success:function(json){
            if(json['done'] === "yes") {
                window.location = "/emailjournal/" + encodeURIComponent(ISSN);

            }
            console.log("Started Fetching");

        },
        error: function (jqXHR, exception) {
            alert("Error occurred, " + jqXHR);
            window.location = "/emailjournal/";
        }
    });

    }
    else {
        alert("ISSN Empty!");
    }



});

function stoploading(e){

    document.getElementById("gethead").remove();
    document.getElementById("loadimg").remove();
}

function showloading(e){


    var a = document.getElementById("loading");
    console.log(a);
    a.firstElementChild.innerHTML = "Getting Information";
    a.lastElementChild.src = "/static/MainApp/Loading_icon.gif";
    a.lastElementChild.height = "100";
    a.lastElementChild.width = "150";
}

function getemails(ISSN, totalCitations){

    $.post('/emailjournal/', {info : ISSN},  function(emails){

        $('#email-list').html(emails);
        var count = $('#Email-Results tr').length - 1;

         html = "<h4><span style='color: orange;'>" + count + "</span> out of <span style='color: coral;'>" + totalCitations + "</span> fetched</h4>";


        $('#totalCitations').html(html);
        if(count === totalCitations)
        {
            stoploading(e);
        }
    });

}

