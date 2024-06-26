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
        $('.input-group.dbdp').each(function() {
            // Add flex-column class
            $(this).addClass('flex-column');
        });
        // Append #gridContainer to the end of the selected fieldset
        if ($('#gridContainer').length === 0) {
            $('#timeslot_form > div > fieldset').append($('<div class="form-row" id="gridContainer"></div>'));
        };

        function initializeCheckAndClick() {
            function checkElementAndClick() {
                // Check if the element is on the DOM
                if ($('#id_date').siblings('.bootstrap-datetimepicker-widget.usetwentyfour').length === 0) {
                    // If the element is not found, click the specified element
                    var targetElement = $('#timeslot_form > div > fieldset > div:nth-child(2) > div > div > div > div');
                    targetElement.click()
                    console.log("click")
                } else {
                    console.log('no click')
                }
            }
    
            // Run the checkElementAndClick function at regular intervals (e.g., every second)
            setInterval(checkElementAndClick, 200);
        }
        // Initialize the check and click functionality
        // initializeCheckAndClick();
        function handleDateChange() {
            // $.ajax({
            //     url:"/appointments/get_contracts/",
            //     type:"POST",
            //     data:{user_field_agent_id: $(this).val(),},
            //     dataType: "json",
            //     success: function(result) {
            //         var $select = $("#id_contract");
            //         var $label = $('label[for="id_contract"]');
            //         $select.empty()
            //         if (result.contracts && result.contracts.length > 0) {
            //             $.each(result.contracts, function(index, contract) {
            //                 $select.append(
            //                     $('<option></option>')
            //                         .attr('value', contract.value)
            //                         .text(contract.text)
            //                 );
            //             });
            //             if (result.contracts.length > 1) {
            //                 $label.text('Contract ('+result.contracts.length+"):");
            //             } else {
            //                 $label.text("Contract:");
            //             }
            //         } else {
            //             $select.append('<option value="" selected="">---------</option>');
            //             $label.text("Contract:");
            //         }
            //     },
            //     error: function(e){
            //         console.error(JSON.stringify(e));
            //     },
            // });
        }
        $('#id_date').parent().on('dp.change', ev => {
            // var  = $('.submit-row input[type="submit"]').prev().last()
            
            // var styleElement = $('<style></style>').text(customBtnStyle);
            // $('head').append(styleElement);
            
            function addCalendarAfter(HTMLSelector) {
                // Days of the week
                async function retrieveAvailabilityData() {
                    function getDateFromPage(ev) {
                        var target = $(ev.target)[0];
                        if (target && typeof target === 'object') {
                            var dateValue = Object.values(target).find(obj => obj && typeof obj === 'object' && obj.hasOwnProperty('date'))?.date;
                            if (dateValue !== undefined) {
                                console.log('Date:', dateValue);
                            } else {
                                console.log('No object with date attribute found in jQuery data.');
                            }
                        } else {
                            console.log('No valid jQuery data found on target.');
                        }
                        return dateValue
                    }
                    var selectedDate = getDateFromPage(ev)
                    var userId = $('#id_user').val();
                    return new Promise(function(resolve, reject){
                        $.ajax({
                            url: '/availability/retrieve_time_slots/',
                            method: 'GET',
                            data: {
                                user_id: userId,
                                date: selectedDate
                            },
                            success: function(data) {
                                // Handle the returned data (list of TimeSlot objects) as needed
                                resolve(data);
                                // Example: Update UI to display retrieved TimeSlots
                            },
                            error: function(err) {
                                reject(err);
                            }
                        });

                    })
                }
                function formatDateString(dateStr) {
                    // Parse the date string into a Date object
                    var date = new Date(dateStr);
                    
                    // Define arrays for days of the week and short month names
                    var daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
                    var shortMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                    
                    // Get day of the week and month abbreviation
                    var dayOfWeekAbbr = daysOfWeek[date.getDay()];
                    var monthAbbr = shortMonths[date.getMonth()];
                    
                    // Get day of the month
                    var dayOfMonth = date.getDate();
                    
                    // Format the result string
                    var formattedDate = dayOfWeekAbbr + ' (' + monthAbbr + ' ' + dayOfMonth + ')';
                    
                    return formattedDate;
                }
                function toggleTimeSlot(userId, date, time) {
                    return new Promise(function(resolve, reject) {
                        // Send date and time data to the view via AJAX
                        $.ajax({
                            url: '/availability/toggle_time_slot_by_user/',
                            method: 'POST', // Adjust method as needed (POST, GET, etc.)
                            data: {
                                date: date,
                                time: time,
                                userId: userId
                            },
                            success: function(response) {
                                // console.log('Data sent successfully:', response);
                                resolve(response); // Resolve promise with response data
                            },
                            error: function(err) {
                                // console.error('Error sending data:', err);
                                reject(err); // Reject promise with error object
                            }
                        });
                    });
                }
                function buildCalendarTable(HTMLSelector, weekStart, hoursList, availableDateTimes) {
                    $(HTMLSelector).empty();
                    var tableContainer = $('<div id="tableContainer"></div>')
                    tableContainer.on('click', 'button.btn', function() {
                        // Get date and time from the clicked button's data attributes
                        element = $(this)
                        var date = element.attr('data-date');
                        var time = element.attr('data-time');
                        var userId = $('#id_user').val();
                    
                        // Toggle the time slot asynchronously
                        toggleTimeSlot(userId, date, time)
                            .then(function(response) {
                                // Handle success response
                                console.log('Toggle successful:', response)
                                element.toggleClass('btn-outline-primary')
                                element.toggleClass('btn-success')
                                // Optionally update UI based on success
                            })
                            .catch(function(error) {
                                // Handle error
                                console.error('Toggle failed:', error);
                                // Optionally update UI to indicate failure
                            });
                    });
                    $(HTMLSelector).append(tableContainer);

                    var table = $('<table class="table table-bordered"></table>').appendTo(tableContainer);
                    var thead = $('<thead></thead>').appendTo(table);
                    var tbody = $('<tbody></tbody>').appendTo(table);
                
                    // Create table header row (days of the week)
                    var headerRow = $('<tr></tr>').appendTo(thead);
                    for (var i = 0; i < 7; i++) {
                        var currentDate = new Date(weekStart);
                        currentDate.setDate(currentDate.getDate() + i + 1);
                        $('<th scope="col">' + formatDateString(currentDate.toISOString().split('T')[0]) + '</th>').appendTo(headerRow);
                    }
                
                    // Create table body rows
                    for (var idx = 0; idx < hoursList.length; idx++) {
                        var hour = hoursList[idx];
                        var tr = $('<tr></tr>').appendTo(tbody);
                        for (var col = 0; col < 7; col++) {
                            var currentDate = new Date(weekStart);
                            currentDate.setDate(currentDate.getDate() + col);
                            var formattedDate = currentDate.toISOString().split('T')[0];
                            var ampm = hour >= 12 ? 'PM' : 'AM';
                            var displayHour = hour > 12 ? hour - 12 : hour;
                            if (displayHour === 0) displayHour = 12; // Handle midnight (0 hour)
                            var buttonLabel = displayHour + ' ' + ampm;
                            var button = $('<button type="button" class="btn"></button>').text(buttonLabel);
                            var source = "none"
                            isAvailable = false
                            for (var i = 0; i < availableDateTimes.length; i++) {
                                if (availableDateTimes[i].date === formattedDate && availableDateTimes[i].time === hour) {
                                    isAvailable = true
                                    source = availableDateTimes[i].source
                                } 
                            }
                            if (isAvailable) {
                                if (source === 'system') {
                                    button.addClass('btn-success'); // Add a class for styling or further identification
                                } else if (source === 'user') {
                                    button.addClass('btn-warning')
                                } else {
                                    button.addClass('btn-outline-primary'); // Add a class for styling or further identification
                                }
                            } else {
                                button.addClass('btn-outline-primary'); // Add a class for styling or further identification
                            }
                            button.attr('data-date', formattedDate); // Store date in data attribute
                            button.attr('data-time', hour); // Store date in data attribute
                            $('<td></td>').append(button).appendTo(tr); 
                            // $('<td><button type="button" class="btn btn-primary">' + buttonLabel + '</button></td>').appendTo(tr);
                        }
                    }
                }
                
                // Example usage:
                // var weekStart = "2024-06-09";  // Replace with your dynamic week start date
                // var hoursList = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21];
                // buildCalendarTable('#gridContainer', weekStart, hoursList);
                
                retrieveAvailabilityData()
                .then(function(data){
                    console.log(data)
                    buildCalendarTable('#gridContainer', data.week_start, data.possible_hours, data.available_times)
                })
                .catch(function(err){
                    console.error('Error fetching data:', err);
                })
                
            }
            addCalendarAfter('#id_user')
            
        });
    }); 
});

