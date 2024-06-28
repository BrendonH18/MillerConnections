window.onload = function() {
    jQuery(function($) {

        // Function to get a specific cookie by name
        const getCookie = name => {
            const cookie = document.cookie.split('; ').find(row => row.startsWith(name + '='));
            return cookie ? decodeURIComponent(cookie.split('=')[1]) : null;
        };

        // Get CSRF token from cookies
        const csrftoken = getCookie('csrftoken');

        // Function to check if a method is CSRF safe
        const csrfSafeMethod = method => /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);

        // Set up AJAX with CSRF token for non-safe methods
        $.ajaxSetup({
            beforeSend: (xhr, settings) => {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });

        $(document).ready(() => {
            // Add 'flex-column' class to elements with 'input-group dbdp' class
            $('.input-group.dbdp').addClass('flex-column');

            // Append a div with id 'gridContainer' if it doesn't exist
            if ($('#gridContainer').length === 0) {
                $('#timeslot_form > div > fieldset').append('<div class="form-row" id="gridContainer"></div>');
            }

            // Initialize datetime picker
            $('#id_date').datetimepicker();

            // Event handler for date change
            const handleDateChange = (ev) => {

                // Function to retrieve availability data
                const retrieveAvailabilityData = (ev) => {
                    let selectedDate = "";
                    if ($(ev.target)[0].id == 'id_user') { 
                        selectedDate = $('#id_date').val(); 
                    }
                    if ($(ev.target)[0].id == 'id_date') { 
                        selectedDate = $(ev.target)[0] && Object.values($(ev.target)[0]).find(obj => obj?.date)?.date; 
                    }

                    const userId = $('#id_user').val();

                    return new Promise((resolve, reject) => {
                        $.ajax({
                            url: '/availability/retrieve_time_slots/',
                            method: 'GET',
                            data: { user_id: userId, date: selectedDate },
                            success: resolve,
                            error: reject
                        });
                    });
                };

                // Function to format date string
                const formatDateString = dateStr => {
                    const date = new Date(dateStr);
                    const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
                    const shortMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                    return `${daysOfWeek[date.getDay()]} (${shortMonths[date.getMonth()]} ${date.getDate()})`;
                };

                // Function to toggle time slot
                const toggleTimeSlot = (userId, date, time, territoryId) => {
                    return new Promise((resolve, reject) => {
                        $.ajax({
                            url: '/availability/toggle_time_slot_by_user/',
                            method: 'POST',
                            data: { date, time, userId, territoryId },
                            success: resolve,
                            error: reject
                        });
                    });
                };

                // Function to get first matching slot
                const getFirstMatching = (availableDateTimes, date) => {
                    const match = availableDateTimes.find(slot => slot.date === date);
                    return match ? match : null;
                };

                // Function to build calendar table
                const buildCalendarTable = (HTMLSelector, weekStart, hoursList, availableDateTimes, availableTerritories) => {
                    // Clear the contents of the HTML container
                    $(HTMLSelector).empty();
                
                    // Create the table container and set up click event handler for buttons inside it
                    const tableContainer = $('<div id="tableContainer"></div>').on('click', 'button.btn', function() {
                        const element = $(this);
                        const date = element.data('date');
                        const time = element.data('time');
                        const userId = $('#id_user').val();
                        const territoryId = element.data('territoryId');
                
                        // Validate data attributes
                        if (!date || !time || !userId || !territoryId) {
                            console.error('Missing required data attributes:', { date, time, userId, territoryId });
                            return;
                        }
                
                        // Toggle the time slot
                        toggleTimeSlot(userId, date, time, territoryId)
                            .then(response => {
                                element.data({ source: response.source, territoryId: response.territoryId });
                                element.toggleClass('btn-outline-primary btn-success');
                                // Change button background color based on class
                                if (element.attr('class').includes('btn-outline')) {
                                    element.css('background', 'white');
                                } else {
                                    element.css('background', '');
                                }
                            })
                            .catch(error => console.error('Toggle failed:', error));
                    }).appendTo(HTMLSelector);
                
                    // Create the table structure
                    const table = $('<table class="table table-striped table-hover"></table>').appendTo(tableContainer);
                    const thead = $('<thead></thead>').appendTo(table);
                    const tbody = $('<tbody></tbody>').appendTo(table);
                
                    // Create the first header row for dates
                    const headerRow1 = $('<tr></tr>').appendTo(thead);
                    for (let i = 0; i < 7; i++) {
                        const currentDate = new Date(weekStart);
                        currentDate.setDate(currentDate.getDate() + i + 1);
                        $('<th class="text-center align-middle" scope="col">' + formatDateString(currentDate.toISOString().split('T')[0]) + '</th>').appendTo(headerRow1);
                    }
                
                    // Array to store initial selected values of territory select elements
                    const initialTerritories = [];
                    const headerRow2 = $('<tr></tr>').appendTo(thead);
                
                    // Create the second header row for territory selectors
                    for (let i = 0; i < 7; i++) {
                        const currentDate = new Date(weekStart);
                        currentDate.setDate(currentDate.getDate() + i + 1);
                        const formattedDate = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(currentDate.getDate()).padStart(2, '0')}`;
                
                        // Create a table header cell with a select element
                        const th = $('<th style="height: 70px; vertical-align: middle;" scope="col"></th>').appendTo(headerRow2);
                        const select = $('<select style="height: 40px; vertical-align: middle;" class="form-select"></select>').appendTo(th);
                
                        // Enable or disable the select based on the number of available territories
                        if (availableTerritories.length > 1) {
                            select.removeAttr('disabled');
                        } else {
                            select.attr('disabled', 'disabled');
                        }
                
                        // Add an empty option for no default value
                        $('<option></option>').appendTo(select);
                
                        // Populate the select with available territories
                        availableTerritories.forEach(territory => {
                            const firstMatching = getFirstMatching(availableDateTimes, formattedDate);
                            const option = $('<option></option>')
                                .val(territory.id)
                                .text(territory.name)
                                .appendTo(select);
                            if (firstMatching && territory.id == firstMatching.territory) {
                                option.prop('selected', true);
                            } else if (availableTerritories.length === 1) {
                                option.prop('selected', true);
                            }
                        });
                
                        // Store the initial selected value
                        initialTerritories.push(select.val());
                
                        // Event listener for select change to update buttons and column colors
                        select.on('change', function() {
                            const selectedTerritoryId = $(this).val();
                            const colorMapping = ['#adb5bd', '', '#0dcaf0']; // Colors for different ranks
                            const rank = $(this).find('option').index($(this).find('option:selected'));
                
                            // Update all buttons in this column with the selected territory
                            $(`#gridContainer td:nth-child(${i + 1}) button`).each(function() {
                                $(this).data('territoryId', selectedTerritoryId);
                                $(this).css('background', $(this).hasClass('btn-outline-primary') ? 'white' : '');
                            });
                
                            // Update the background color of the column based on the rank
                            $(`#gridContainer td:nth-child(${i + 1})`).each(function() {
                                $(this).css('background-color', colorMapping[rank] || '');
                            });
                        });
                    }
                
                    // Create table rows for each hour
                    hoursList.forEach(hour => {
                        const tr = $('<tr></tr>').appendTo(tbody);
                        for (let col = 0; col < 7; col++) {
                            const currentDate = new Date(weekStart);
                            currentDate.setDate(currentDate.getDate() + col);
                            const formattedDate = currentDate.toISOString().split('T')[0];
                            const ampm = hour >= 12 ? 'PM' : 'AM';
                            const displayHour = hour > 12 ? hour - 12 : hour || 12;
                
                            // Create a button for each time slot
                            const button = $('<button type="button" class="btn"></button>')
                                .text(`${displayHour} ${ampm}`)
                                .data({ date: formattedDate, time: hour, territoryId: initialTerritories[col], source: ''})
                                .addClass('btn-outline-primary');
                
                            // Update button class based on available date times
                            availableDateTimes.forEach(slot => {
                                if (slot.date === formattedDate && slot.time === hour) {
                                    button.removeClass('btn-outline-primary').addClass(slot.source === 'system' ? 'btn-success' : 'btn-warning');
                                    button.data({ source: slot.source });
                                }
                            });
                
                            // Append the button to the table cell
                            $('<td></td>').append(button).appendTo(tr);
                        }
                    });
                
                    // Trigger change event for each select element to update the buttons and column colors initially
                    $('thead select').each(function() {
                        $(this).trigger('change');
                    });
                };
                

                retrieveAvailabilityData(ev)
                    .then(data => buildCalendarTable('#gridContainer', data.week_start, data.possible_hours, data.available_times, data.available_territories))
                    .catch(err => console.error('Error fetching data:', err));
            };

            // Attach event handlers for date and user changes
            $('#id_date').parent().on('dp.change', handleDateChange);
            $('#id_user').parent().on('change', handleDateChange);
        });
    });
}
