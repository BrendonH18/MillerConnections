jQuery(function($){
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $(document).ready(function(){
        $("#id_user_field_agent").change(function(){
            $.ajax({
                url:"/appointments/get_contracts/",
                type:"POST",
                data:{user_field_agent_id: $(this).val(),},
                dataType: "json",
                success: function(result) {
                    var $select = $("#id_contract");
                    var $label = $('label[for="id_contract"]');
                    $select.empty()
                    if (result.contracts && result.contracts.length > 0) {
                        $.each(result.contracts, function(index, contract) {
                            $select.append(
                                $('<option></option>')
                                    .attr('value', contract.value)
                                    .text(contract.text)
                            );
                        });
                        if (result.contracts.length > 1) {
                            $label.text('Contract ('+result.contracts.length+"):");
                        } else {
                            $label.text("Contract:");
                        }
                    } else {
                        $select.append('<option value="" selected="">---------</option>');
                        $label.text("Contract:");
                    }
                },
                error: function(e){
                    console.error(JSON.stringify(e));
                },
            });
        });
    }); 
});