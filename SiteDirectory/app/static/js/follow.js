$(document).ready(function() {
    // Set CSRF token
    // var csrf_token = $('meta[name=csrf-token]').attr('content');
    // // Configure AJAX so that the CSRF token is added to the header of any request
    // $.ajaxSetup({
    //     beforeSend: function(xhr, settings) {
    //         if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
    //             xhr.setRequestHeader("X-CSRFToken", csrf_token);
    //         }
    //     }
    // });

    // Attach a function to trigger when user submits a follow/unfollow request
    $("a.followBtn").on("click", function() {
        var clicked_obj = $(this);

        // Was follow or unfollow clicked? Fetch button ID
        var user_id = $(this).attr('id');
        // Follow or unfollow?
        var followUnfollow = $(this).children()[0].id;
        // The call which sends data to the server. Captures the data needed to update whether the button should show follow or unfollow
        $.ajax({
            url: '/follow',
            type: 'POST',
            data: JSON.stringify({ user_id: user_id, followUnfollow: followUnfollow} ),

            contentType:"application/json; charset=utf-8",
            dataType: "json",
            success: function(response){
                console.log(response);
                // Update HTML to reflect the user is now following instead of unfollowing (or vice-versa)
                if(followUnfollow == "follow") {
                    clicked_obj.children()[0].classList.add("d-none");
                    document.getElementById("unfollow").classList.remove("d-none");
                }
                else{
                    clicked_obj.children()[0].classList.add('d-none');
                    document.getElementById('follow').classList.remove("d-none");
                }
            },
            error: function(error){
                console.log(error);
            }
        });
    });


});