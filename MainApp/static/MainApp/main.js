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


    var doi = document.getElementById("doiinput").value;
    var totalCitations="(fetching..)", author="-", date="-", titlee="-", citationurl;

    if(doi!=="")
    {
        showloading(e);

        $.ajax({

        type:'GET',
        url:'/totalcitations/',
        timeout : 500000,
        data:{
            q:$('#doiinput').val()
        },

        success:function(json){

            totalCitations = json['totalCitations'];
            titlee = json['title'];
            author = json['author'];
            date = json['date'];
            citationurl = json['citation_urls'];

            CallbackAjaxCall();


        },

        error: function(jqXHR, textStatus, errorThrown) {

            console.log(jqXHR.status + ": " + jqXHR.responseText);

        }

        });


        function CallbackAjaxCall() {

        $.ajax({

        type:'GET',
        url:'/main/',
        data:{
            q:$('#doiinput').val(),
            c:citationurl,
        },

        success:function(json){

            if(json['done'] === "no")
            {
                alert(json['response']);
                window.location = "/main/";
            }

        },
        error: function(jqXHR, textStatus, errorThrown) {
        if(textStatus==="timeout") {
            alert("Call has timed out"); //Handle the timeout
        } else {
            console.log(jqXHR.status + ": " + jqXHR.responseText);
            alert("Some error was returned"); //Handle other error type
        }
    }
    });

        }


    }
    else {
        alert("DOI Empty!");
    }

    var duration = 8000000,
        interval = 8000,
        intervalTimer;

        intervalTimer = setInterval(function() {
            getemails(doi, totalCitations, titlee, author, date);
        }, interval);

        setTimeout(function() {
            clearInterval(intervalTimer);
        }, duration);



});

function stoploading(e){

    document.getElementById("gethead").remove();
    document.getElementById("loadimg").remove();
}

function showloading(e){


    var a = document.getElementById("loading");
    a.firstElementChild.innerHTML = "Getting Information";
    a.lastElementChild.src = "/static/MainApp/Loading_icon.gif";
    a.lastElementChild.height = "100";
    a.lastElementChild.width = "150";
}

function getemails(doi, totalCitations, titlee, author, date){

    $.post('/emails/', {info : doi},  function(emails){
        // console.log(emails);
        $('#email-list').html(emails);
        var count = $('#Email-Results tr').length - 1;

        console.log(totalCitations);
        console.log(titlee);
        console.log(author);
        console.log(date);

        metadata = "<ul> <li> Title : " + titlee + "</li> <li> Author : " + author + "</li> <li> Date : " + date + "</li>";

        html = "<h4><span style='color: orange;'>" + count + "</span> out of <span style='color: coral;'>" + totalCitations + "</span> fetched</h4>";

        html = metadata + html;

        $('#totalCitations').html(html);
        if(count === totalCitations)
        {
            window.location =  "/finalDOI/" + encodeURIComponent(doi);
        }

    });

}

