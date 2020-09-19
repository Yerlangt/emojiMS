$(function() {
    $(document.body.getElementsByClassName("btn-send")[0]).click(function() {
        $.ajax({
            url: '/sendMessage',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
				              const data = JSON.parse(response);
							var dialog = document.body.getElementsByClassName("card-body")[0];
							  dialog.innerHTML += '<div class="d-flex justify-content-end mb-4"><div class="msg_cotainer_send">' + data['message'] + '<span class="msg_time_send">8:55</span></div>';
								
							  
				
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});

